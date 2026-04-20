#!/usr/bin/env python3
"""
Exp 40 Pre-launch Panel Review — Round 3B (final arbitration)
=============================================================

Round 3 closed Q6 unanimously on `star`. Residuals:

  Q3-wiring: 3-2 split — Codex/ChatGPT/DeepSeek (w2) post-hoc; Gemini/CC2
             (w1) runtime. Must converge.
  Q4-lock:   core 7 fields unanimous; field-name variance and enum-value
             variance (`other`, `supported_agreement`) on 3-4 fields.
  Q5-lock:   four-family structure unanimous; perturbation magnitude
             (0.10 vs 0.15), sample rate (10% vs 20%), parameter set
             (2 vs 5), selection strategy (deterministic vs random) vary.

Round 3B mode: CANONICAL DRAFT yield-or-refute. Rather than asking models
to re-propose, Round 3B presents a single canonical answer per residual
(derived from Round 3 convergence under C1-C8) and requires each model
to either APPROVE with reasons or REFUTE with reasons. Under P4 + the
tightened constraints, the most robust single answer wins.

Protocol: CDSFL + FFAFP, Stage 6 math as arbiter, compelled convergence,
          P4 synthesis qualifier, no qualitative opt-out, C1-C8 narrowing.
Models:   Gemini 3.1 Pro, Codex GPT-5.4, CC2 (Opus 4.6), ChatGPT GPT-5.4,
          DeepSeek R1-0528
Dispatch: parallel via ThreadPoolExecutor(max_workers=5)

Round 3 source: confer_exp40_prelaunch_round3, timestamp loaded at runtime.
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

LOGS_DIR = REPO_ROOT / "bench" / "logs" / "confer_exp40_prelaunch_round3b"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

R3_DIR = REPO_ROOT / "bench" / "logs" / "confer_exp40_prelaunch_round3"

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
# Load Round 3 responses
# ---------------------------------------------------------------------------

def _load_round3() -> dict[str, str]:
    combined_files = sorted(R3_DIR.glob("combined_*.json"))
    if not combined_files:
        raise FileNotFoundError(f"No Round 3 combined log found in {R3_DIR}")
    latest = combined_files[-1]
    data = json.loads(latest.read_text(encoding="utf-8"))
    out: dict[str, str] = {}
    for label, payload in data.items():
        if "response" not in payload:
            raise ValueError(f"Round 3 response for {label} missing: {payload.get('error')}")
        out[label] = payload["response"]
    print(f"  loaded Round 3 responses from {latest.name}", flush=True)
    return out


R3_RESPONSES = _load_round3()

# ---------------------------------------------------------------------------
# Prompt components
# ---------------------------------------------------------------------------

STAGE6_MATH = r"""
## CDSFL Stage 6 — Unified Self-Assessment Equation (canonical)

    R_k(i) = R_k(i-1) * (1 - q) / (1 - q * R_k(i-1))
    q     = eta * d * p
    eta_combined = eta_int * (1 - c_ext * (1 - nu_k))
    m_div in {1.00, 0.85, 0.70, 0.60}
    eta_int_modulated = m_div * eta_int
"""

STANDING_POLICY = r"""
## Standing policy (founder directives, 2026-04-20)

P1. Shadow-promotion-now — activate now, defer only on demonstrable harm.
P2. Runner v1 preservation — v1 default for Exp 40; v2 promotion blocked.
    Runtime behavior change in Exp 40 is forbidden unless demonstrably
    necessary.
P3. 15 experiments — Exp 40-53 components + Exp 54 integration.
P4. Synthesis qualifier — synthesis only if demonstrably better than best
    single; otherwise pick most robust / most flexible.
"""

NEW_CONSTRAINTS = r"""
## Round 3 constraints (unchanged)

C1 efficiency. C2 rational (human + machine). C3 robust (non-gameable).
C4 effective. C5 human UX seamlessness. C6 third-party defensibility.
C7 internally + externally self-consistent. C8 fits CDSFL schema.
"""

R3B_INSTRUCTION = r"""
## Round 3B instruction — canonical-draft arbitration

Round 3 left residuals on Q3-wiring (3-2 split), Q4-lock (field-name
and enum-value variance), and Q5-lock (numeric-constant and
perturbation-protocol variance). Q6-lock is unanimous on `star`.

Round 3B presents a CANONICAL DRAFT ANSWER per residual question. For
each residual:

  * APPROVE — state "APPROVE Q<N>", then give one-paragraph reasons
    citing the specific C1-C8 constraints the canonical draft
    satisfies.

  * REFUTE — state "REFUTE Q<N>", include a LITERAL QUOTED SUBSTRING
    from the canonical draft that is wrong or weaker than an
    alternative, name the specific C1-C8 constraint(s) it fails,
    quote your counter-proposal in full, and explain why your
    counter-proposal demonstrably better satisfies the constraints
    than the canonical draft.

  * Partial refutation: state "REFUTE Q<N> (partial)" and itemise
    which elements of the canonical draft you approve and which you
    refute, with quoted substrings for each refutation.

You may NOT produce menus of alternatives. You must converge on a
single answer per question. P4 applies: a counter-proposal is accepted
only if demonstrably better than the canonical draft; otherwise the
canonical draft is the robust single answer.

Mechanical compliance: any literal quote must be a literal substring
of the canonical draft text below or of a named peer's Round 3 answer.
"""

# ---------------------------------------------------------------------------
# Canonical drafts (derived from Round 3 convergence)
# ---------------------------------------------------------------------------

CANONICAL_Q3 = r"""
## Canonical draft Q3-wiring

ANSWER: (w2) — computed only in post-hoc analysis after Exp 40 completes.
Not wired into runtime.

RATIONALE under C1-C8 and P2/P4:

- C7 (consistency) and P2 (runner v1 preservation): Exp 40 is the
  preservation run. Any new runtime code path — even one that only
  emits a boolean flag — changes v1's runtime behavior and confounds
  the preservation evidence. Post-hoc computation from already-logged
  Stage 6 parameters preserves v1 runtime exactly.
- C1 (efficiency): Post-hoc is O(n) over findings during report
  generation, zero hot-path cost. Runtime (w1) is O(1) per finding but
  non-zero. Under C1, zero cost beats near-zero cost when the
  epistemic effect is identical.
- C6 (third-party defensibility): Post-hoc computation is reproducible
  by any reviewer holding the Exp 40 log and the declared R_min
  policy. Runtime flag would require reviewers to trust that the
  runner's computation was not itself defective.
- P4 (synthesis qualifier): (w2) is the more robust single answer;
  (w1) claims zero-cost "flag only" but still introduces new runtime
  code. Under P4, robust single wins absent demonstrated superiority
  of the alternative — and no such demonstration exists for (w1) in
  the preservation context.

Post-hoc fields (computed during report generation, not stored in
runtime telemetry):
  - r_min_policy (float) — session-level configured validity floor
  - nu_max_for_r_min (float) — derived per-finding from logged
    eta_int, d, p, c_ext, r_k_before
  - exceeds_nu_max (bool) — derived: nu_k > nu_max_for_r_min

Used in the Exp 40 report for: (a) admissibility-gap stratification,
(b) correlation with later refutation/admissibility outcomes,
(c) evidence input for an Exp 41+ decision on whether a runtime guard
is justified.
"""

CANONICAL_Q4 = r"""
## Canonical draft Q4-lock (unified reason-trace schema, exact 10 fields)

| # | field_name                 | type                                            | value constraint / validator                                                                  | required condition                                | human gloss                                                                             |
|---|----------------------------|-------------------------------------------------|-----------------------------------------------------------------------------------------------|---------------------------------------------------|-----------------------------------------------------------------------------------------|
| 1 | issue_id                   | string                                          | non-empty, snake_case; unique within round                                                    | always                                            | which divergence point this row is about                                                |
| 2 | stance                     | enum[yield, refute, unchanged]                  | exact enum                                                                                     | always                                            | what the model did on this point                                                         |
| 3 | target_model_id            | enum[gemini, codex, cc2, chatgpt, deepseek, none] | `none` iff stance == unchanged; else one of the five panel model ids                           | always                                            | which peer is being answered (or `none` for unchanged)                                   |
| 4 | target_quote_literal       | string                                          | LITERAL SUBSTRING of cited peer's prior-round answer; non-empty if present                    | required if stance in {yield, refute}              | exact peer text being answered                                                           |
| 5 | reason_type                | enum[math_error, logical_gap, unsupported_assumption, scope_error, corrected_misread, tool_output] | exact enum; NO `other`; NO `supported_agreement`. Unchanged = reason_type null.                 | required if stance in {yield, refute}              | which epistemic failure mode applies                                                     |
| 6 | reason_text                | string                                          | non-empty, minimum 20 chars; plain-language causal explanation                                 | required if stance in {yield, refute}              | why the yield or refute happened                                                          |
| 7 | prior_position_hash        | string                                          | sha256 hex of canonical JSON of this model's pre-round position on this issue_id              | always                                            | locked prior position snapshot                                                            |
| 8 | new_position_hash          | string                                          | sha256 hex of canonical JSON of this model's post-round position on this issue_id             | always                                            | locked post-round position snapshot                                                       |
| 9 | state_delta                | dict                                            | keys = Stage 6 / claim parameter names; values = {"before": scalar, "after": scalar}; empty dict iff prior_position_hash == new_position_hash | always (may be empty)                              | what substantively changed (scalar-keyed diff, no free text)                             |
| 10 | compliance_risk_flag      | bool                                            | DERIVED at runner post-processing: True iff stance == yield AND any of (target_quote_literal is not a substring of cited peer, prior_position_hash == new_position_hash, state_delta is empty, reason_text is missing or <20 chars, reason_type is null) | always                                            | flags mechanically compliant yields for founder review                                   |

Exact conventions:
- `issue_id` is snake_case and stable across rounds for the same point.
- `target_model_id` uses canonical five-element enum plus `none`; exact
  string values are `gemini`, `codex`, `cc2`, `chatgpt`, `deepseek`,
  `none`.
- `reason_type` enum has exactly six values; `other` and
  `supported_agreement` are EXCLUDED because they undermine
  machine-checkability and audit defensibility.
- `compliance_risk_flag` is a DERIVED field computed by runner
  post-processing from the other nine fields; it is not trusted to
  the writing model.
- `state_delta` is a scalar-keyed dict; narrative explanation belongs
  in `reason_text`, not here.

Compliance predicate (runner-computed):
```
compliance_yield = (
    stance == "yield"
    and (
        target_quote_literal not in cited_peer_prior_round_answer
        or prior_position_hash == new_position_hash
        or len(state_delta) == 0
        or not reason_text or len(reason_text) < 20
        or reason_type is None
    )
)
```
"""

CANONICAL_Q5 = r"""
## Canonical draft Q5-lock (v1 preservation — four families, exact)

### Family 1: Math-path fidelity
LOG FIELDS (per-dispatch):
  - stage6_path_used: bool
  - forbidden_pattern_hits: int
  - r_k_before: float in [0,1]
  - r_k_after: float in [0,1]
  - eta_int: float in [0,1]
  - m_div: float in {1.00, 0.85, 0.70, 0.60}
  - nu_k: float in [0,1]
  - c_ext: float in [0,1]
  - eta_combined: float in [0,1]
  - q: float in [0,1]

PREDICATE (per-dispatch):
  accept_math_path_fidelity = (
      stage6_path_used
      and forbidden_pattern_hits == 0
      and 0.0 <= r_k_before <= 1.0
      and 0.0 <= r_k_after  <= 1.0
      and 0.0 <= eta_int    <= 1.0
      and m_div in {1.00, 0.85, 0.70, 0.60}
      and 0.0 <= nu_k       <= 1.0
      and 0.0 <= c_ext      <= 1.0
      and 0.0 <= eta_combined <= 1.0
      and 0.0 <= q          <= 1.0
  )

EXPERIMENT-LEVEL:
  experiment_accept_math_path_fidelity = (
      count(accepted_dispatch where not accept_math_path_fidelity) == 0
  )

HUMAN GLOSS: every accepted finding traversed the canonical Stage 6
path with in-range values.

### Family 2: Correction fidelity
LOG FIELDS (per-round):
  - upstream_revision_count: int
  - downstream_revisit_count: int
  - unresolved_divergence_count: int

PREDICATE:
  accept_correction_fidelity = (
      (upstream_revision_count == 0 and downstream_revisit_count == 0)
      or (upstream_revision_count > 0 and downstream_revisit_count >= upstream_revision_count)
  )

HUMAN GLOSS: when upstream claims changed, downstream dependents were
revisited at least once each.

### Family 3: Counterfactual sensitivity
LOG FIELDS (per-experiment):
  - counterfactual_probe_applicable_count: int
  - counterfactual_probe_run_count: int
  - counterfactual_r_changed_count: int
  - counterfactual_action_changed_count: int

PERTURBATION PROTOCOL:
  - Parameters perturbed: eta_int AND nu_k, one at a time.
  - Magnitude: +/- 0.10 absolute, clamped to [0, 1].
  - Selection: deterministic stride — every 10th applicable dispatch
    (first applicable dispatch included), minimum 1.
  - Execution: runner replays the dispatch with the perturbed
    parameter; records r_k_after_perturbed and action_after_perturbed.
  - Sensitivity: perturbation counts if
    abs(r_k_after - r_k_after_perturbed) > 1e-9
    OR action_after != action_after_perturbed.

PREDICATE:
  accept_counterfactual_sensitivity = (
      counterfactual_probe_run_count >= max(1, counterfactual_probe_applicable_count // 10)
      and (counterfactual_r_changed_count + counterfactual_action_changed_count) >= 1
  )

HUMAN GLOSS: at least one probed dispatch showed the mathematics
actually drove the outcome; math is load-bearing, not ornamental.

### Family 4: Convergence stability
LOG FIELDS:
  - unresolved_divergence_count[round]: int (per-round, indexed)
  - late_reversal_count: int (per-experiment, events after Round 3)
  - reasoned_yield_count: int (per-round; yields where compliance_risk_flag == False)
  - compliance_yield_count: int (per-round; yields where compliance_risk_flag == True)

PREDICATE:
  accept_convergence_stability = (
      unresolved_divergence_count[round_1] >= unresolved_divergence_count[round_2]
      and unresolved_divergence_count[round_2] >= unresolved_divergence_count[round_3]
      and unresolved_divergence_count[final_round] == 0
      and late_reversal_count == 0
      and reasoned_yield_count_final >= compliance_yield_count_final
  )

HUMAN GLOSS: disagreement shrank monotonically, the final lock held,
and reasoned movement dominated compliance movement.

### Experiment-level preservation decision
accept_v1_preservation = (
    experiment_accept_math_path_fidelity
    and accept_correction_fidelity
    and accept_counterfactual_sensitivity
    and accept_convergence_stability
)

All predicates are deterministic, O(1) or O(n) over already-logged
fields. No probabilistic classifier. No embedding dependency. No
free-parameter tuning.
"""

# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

def build_prompt(self_label: str) -> str:
    self_display = LABEL_DISPLAY[self_label]
    self_r3 = R3_RESPONSES[self_label]
    peer_blocks = []
    for peer_label in ("gemini", "codex", "cc2", "chatgpt", "deepseek"):
        if peer_label == self_label:
            continue
        peer_display = LABEL_DISPLAY[peer_label]
        peer_r3 = R3_RESPONSES[peer_label]
        peer_blocks.append(f"""\
### PEER R3 ANSWER — {peer_display}

{peer_r3}
""")
    peer_section = "\n---\n\n".join(peer_blocks)

    return f"""\
# Exp 40 Pre-launch Panel Review — Round 3B (final arbitration)

You ({self_display}) have completed Round 2A, Round 2B, and Round 3.
Q6-lock converged unanimously on `star`. Residuals remain on Q3-wiring
(3-2 split), Q4-lock (field-name and enum-value variance), and Q5-lock
(numeric-constant and perturbation-protocol variance).

Round 3B: the panel must converge on a single answer per residual.
Canonical drafts are presented below. For each residual question,
APPROVE or REFUTE (partial or full) with literal quoted substrings and
C1-C8 reasons. No menus. P4 applies.

---

{STAGE6_MATH}

---

{STANDING_POLICY}

---

{NEW_CONSTRAINTS}

---

{R3B_INSTRUCTION}

---

{CANONICAL_Q3}

---

{CANONICAL_Q4}

---

{CANONICAL_Q5}

---

## YOUR R3 ANSWER — {self_display}

{self_r3}

---

{peer_section}

---

## Charge for Round 3B

For Q3-wiring, Q4-lock, and Q5-lock, state APPROVE or REFUTE (partial
or full) with literal quoted substrings and C1-C8 reasons. If you
refute any element, give the exact alternative text in full and
demonstrate why it better satisfies C1-C8. If you approve, state so
concisely. Word budget: up to 1,500 words across the three answers.
Do not re-litigate Q6-lock — it is unanimous.
"""


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
    print("  EXP 40 PRE-LAUNCH PANEL REVIEW — Round 3B (final arbitration)")
    print(f"  Timestamp: {ts}")
    print("  Protocol: CDSFL + FFAFP, canonical-draft yield-or-refute")
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
