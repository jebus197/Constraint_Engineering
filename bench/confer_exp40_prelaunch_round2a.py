#!/usr/bin/env python3
"""
Exp 40 Pre-launch Panel Review — Round 2A of 3
==============================================

Five-model (star-topology) follow-up to Round 1 (2026-04-20), with
COMPELLED CONVERGENCE discipline applied and the founder's four
standing corrections included in the brief.

Round 2A charge: each model answers six questions in isolation with
full workings. A subsequent Round 2B dispatch will show each model
the four other Round 2A answers and require yield-with-reasons or
refute-with-reasons on each divergent point.

Protocol: CDSFL + FFAFP, Stage 6 math as arbiter, compelled convergence,
          no qualitative opt-out.
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

LOGS_DIR = REPO_ROOT / "bench" / "logs" / "confer_exp40_prelaunch_round2a"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

MODELS = [
    ("gemini",   "gemini-3.1-pro-preview",     "gemini_native"),
    ("codex",    "openai/gpt-5.4",             "openrouter"),
    ("cc2",      "opus",                       "claude_cli"),
    ("chatgpt",  "openai/gpt-5.4",             "openrouter"),
    ("deepseek", "deepseek/deepseek-r1-0528",  "openrouter"),
]

# ---------------------------------------------------------------------------
# System prompt: full CDSFL formal core
# ---------------------------------------------------------------------------

CDSFL_PATH = REPO_ROOT / "bench" / "directives" / "universal" / "cdsfl_core_formal.md"
CDSFL_TEXT = CDSFL_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# Stage 6 canonical math block (V6)
# ---------------------------------------------------------------------------

STAGE6_MATH = r"""
## CDSFL Stage 6 — Unified Self-Assessment Equation (canonical)

### Recursive state

    R_k(i) = R_k(i-1) * (1 - q) / (1 - q * R_k(i-1))
    q     = eta * d * p

### Stage 6 eta decomposition (literature-calibrated novelty)

    eta_combined = eta_int * (1 - c_ext * (1 - nu_k))

where:
    eta_int  in [0,1]   internal novelty (within session)
    nu_k     in [0,1]   literature novelty (per-finding, Ouroboros)
    c_ext    in [0,1]   source-diversity corroboration = 1 - prod_s (1 - c_s)

### Orthogonality (load-bearing)

    R_k    measures VALIDITY
    nu_k   measures NOVELTY
    c_ext  measures SEARCH QUALITY

The three are independent reporting dimensions; MUST NEVER be collapsed
into a single score before reporting.

### Divergence modulator channel (round-2 unanimous, round-3 verified)

    m_div in {1.00, 0.85, 0.70, 0.60}
    eta_int_modulated = m_div * eta_int
    eta_combined = eta_int_modulated * (1 - c_ext * (1 - nu_k))
    q = eta_combined * d * p
    R_k(i) = R_k(i-1) * (1 - q) / (1 - q * R_k(i-1))

    FORBIDDEN: m_div as pre-factor on R_k.
    FORBIDDEN: m_div counting toward nu_k.
    FORBIDDEN: w(f) in q_eff.
"""

# ---------------------------------------------------------------------------
# FFAFP 5-step pattern (in user prompt)
# ---------------------------------------------------------------------------

FFAFP = r"""
## FFAFP — Find, Follow, Analyse, Fix, P-pass

FIND: identify the issue, what is wrong, where, and what evidence.
FOLLOW: trace consequences through the system before touching anything.
ANALYSE: use available tools (SymPy, z3, NumPy, SciPy, Wolfram, etc.).
        Tool output IS the evidence. Do not substitute reasoning for tool output.
FIX: propose the simplest sufficient correction addressing root cause +
     downstream consequences.
P-PASS: falsify your own proposed fix. State what could make it wrong.

Follow comes before Fix. Find without Follow produces shallow patches.
Fix without Follow produces regressions.
"""

# ---------------------------------------------------------------------------
# Compelled convergence preamble (new for Round 2)
# ---------------------------------------------------------------------------

CONVERGENCE = r"""
## Compelled convergence (new for Round 2)

Each question must receive ONE definitive answer with full workings shown.

This is Round 2A (isolated star dispatch). Round 2B will follow, in which
you will be shown the Round 2A answers from the four other models. In
Round 2B, on each point where your Round 2A answer differs from another
model's, you must either:

  (1) YIELD WITH EXPLICIT REASONS — state which model, what in their
      reasoning made you change your position, and why their reasoning
      is stronger than yours was.

  (2) REFUTE WITH EXPLICIT REASONS — state which model, what in their
      reasoning is wrong or incomplete, and why your position is
      stronger than theirs.

A yield without reasons is a non-answer and will be rejected in
post-processing. Producing a menu of options for the founder to choose
from is not acceptable. The panel's job is to arrive at the answer,
not to pre-sort a multiple-choice for human selection.

## No qualitative opt-out

Where a question admits a quantitative answer, qualitative framing is not
an acceptable substitute. The Stage 6 equation is the constraint box. If
you cannot answer quantitatively, state precisely what empirical input
is missing; do not substitute qualitative language for the missing
quantification.
"""

# ---------------------------------------------------------------------------
# Standing-policy block (founder directives, 2026-04-20)
# ---------------------------------------------------------------------------

STANDING_POLICY = r"""
## Standing policy (founder directives, 2026-04-20)

These four standing corrections have been issued since Round 1 and apply
to Round 2 and all subsequent work. They are not questions for the panel.
They are the context within which the panel answers.

### P1. Shadow-promotion-now

For any element currently in shadow mode (computed and logged but not
affecting outcomes) and for any broken or non-functioning tool, the
default is to ACTIVATE or REPAIR NOW, not defer. This applies unless a
specific element is demonstrably likely to cause harm within the
Exp 40-53 window. Elements that will have no meaningful impact until
Bench Run 2 should still be enabled now, so that any troubleshooting
happens while context and founder memory on the component are fresh.

Reason: context-boundedness of LLMs across compactions and founder-side
memory drift over a multi-month project means deferring activation to
"the experiment that exercises it" is likely to produce larger
downstream costs than early activation. Almost every element in the
current inactive set has already passed multi-model panel review.

### P2. Runner v1 preservation

Runner v1 remains the default for Exp 40. The Round 1 panel's unanimous
promote-to-v2 recommendation was overruled by the founder.

Reason: Runner v1 is the first and currently only runner with a
live-demonstrated, instrumented convergence where the panel models
can be shown to have used the mathematical model throughout their
reasoning chains. This is load-bearing empirical evidence the Round 1
panel did not have access to. Additionally, if Exp 40 and its
successors prove the framework capable of generating meaningful novelty
beyond code during Bench Run 2, v1 acquires historical and cultural
value in its own right. Test-count parity (v2's 1,250 tests) is
necessary but not sufficient for promotion; experiment-level parity is.

### P3. The plan has 15 experiments

Exp 40 through 53 are 14 COMPONENT studies, each examining a distinct
aspect of the framework. Exp 54 is 1 integration round. Total: 15
experiments, not "Exp 54 integration".

When a proposed behavioural decision would be deferred to Exp 54,
consider whether one of the 13 intervening component experiments is the
correct landing zone first.

### P4. Synthesis qualifier

When a synthesis of two or more positions is proposed, the synthesis
must be DEMONSTRABLY BETTER than the best single position in isolation.
If the demonstration is not possible (i.e., no concrete case where the
synthesis outperforms the best single), choose the MOST ROBUST / MOST
FLEXIBLE single position from those available, with reasons.

Do not default to "composite of multiple positions" without
demonstration. A composite without demonstration is a menu in disguise.
"""

# ---------------------------------------------------------------------------
# Round 1 summary (for continuity — condensed, not verbose)
# ---------------------------------------------------------------------------

ROUND1_SUMMARY = r"""
## Round 1 summary (for continuity)

### Unanimous (5/5)

- Mathematics verifier sandbox is broken and must be fixed before launch.
  (exec with global_dict={'__builtins__': {}} blocks Integer parsing;
  every symbolic check returns UNCERTAIN silently.)

- The DCY continuous-divergence formula proposed in an earlier round is
  REJECTED, on four independent grounds: multiplicative double-count
  with existing gamma/rho; no empirical calibration target; Deps(.) is
  not part of the canonical framework (Appendix section 7.12 covers
  aggregate defect-flux D_{n+1} = nu*D_n + epsilon_n, not per-finding
  dependencies); continuous penalty undermines the already-decided
  discrete m_div in {1.00, 0.85, 0.70, 0.60}. Gemini (original proposer)
  self-retracted.

- Star topology retained as Round 2 discipline.

- Rounds 2 and 3 should be triggered.

### 4/5 (one dissent each)

- Star-with-paired-challenge endorsed as Exp 41+ variant (Gemini
  dissented on complexity).

- Multi-domain verification raises effective passage probability via
  p_eff = 1 - prod(1 - p_j).

- 1E.10 runtime assertion at reference_runner_v2.py:3510 deferred to
  Exp 54 (Gemini dissented: activate now with m_div = 1.0 hardcoded).

### Divergent (Round 2 must converge)

- M1 priority order: D -> B -> C (Codex, ChatGPT); B -> D -> C (CC2);
  unspecified (Gemini, DeepSeek). D and C are now resolved outside the
  panel (D = decision; C = overruled). Only B is live work.

- Verdict combination: first-definitive + contradiction veto (Codex,
  ChatGPT) vs confidence-weighted aggregation (Opus, DeepSeek).

- EMA half-life for B-cell telemetry: 50 dispatches (3/5) vs 20-30
  (ChatGPT) vs unspecified (others).

- n_min for B-cell activation: 10 (Opus, DeepSeek); 20 (CC2); 30 (Codex).

- Novelty-vs-hallucination boundary: empirical fit required (4/5) vs
  derivable from Stage 6 (Gemini only, self-marked [SPECULATIVE]).

- M/N correctness-ratio status: shadow diagnostic (some); display
  alongside validity (some); absorbed into validity (some).

### Math claims verified (CC1 sy + Wolfram cross-check)

- sim_max = 43/50 = 0.86 CONFIRMED (Appendix 1.3).
- p_eff = 1 - prod(1 - p_j) monotone in N under independence CONFIRMED.
- Stage 6 dR_next/dq = R(R-1)/(1-qR)^2 < 0 on (0,1)^2 CONFIRMED (strict).
- EMA half-life h yields alpha = 1 - 2^(-1/h); (1 - alpha)^h = 1/2
  symbolically (Wolfram) CONFIRMED for all h > 0.
- DCY double-penalty (third redundant factor) CONFIRMED symbolically.
- Opus's SymPy parse_expr + local_dict whitelist CONFIRMED functional
  on 6/6 test cases (replaces broken exec sandbox).
"""

# ---------------------------------------------------------------------------
# Round 2 questions (six)
# ---------------------------------------------------------------------------

QUESTIONS = r"""
## Round 2 questions (six; each requires single definitive answer + workings)

### Q1. Activation sequence under shadow-promotion-now

Items to activate (all have passed Round 1 review to the level of
necessary consensus or founder directive P1):

  (i)   SMT sandbox fix — replace
          exec(code, global_dict={'__builtins__': {}}, {})
        with parse_expr(code, local_dict=WHITELIST, transformations=...),
        where WHITELIST contains 9 identifiers: Integer, Rational, Symbol,
        sin, cos, exp, log, sqrt, pi. 6/6 test cases pass on CC1's rig.

  (ii)  1E.10 runtime assertion at reference_runner_v2.py:3510 —
        replace bare compute_rk call with compute_rk_with_eta_channel
        wrapper, m_div hardcoded to 1.0 with log tag "gated-shadow:
        m_div=1.0 hardcoded until wiring event". When m_div wiring lands
        in a later experiment, the log tag makes the hardcode visible
        at review.

  (iii) K/L/M specialist cells flip — single-line edit at
        immune_agents.py:334 to extend LIVE_SPECIALIST_DOMAINS from
        {mathematics, statistics, biology, information_science} to
        {mathematics, statistics, biology, information_science, physics,
         chemistry, engineering}. Shadow-wired cells (1E.4) become live.
        K/L/M share the immune dispatcher — potential correlated failure.

Questions:
  (a) What is the correct activation sequence among {(i), (ii), (iii)}?
      Must avoid correlated failures; K/L/M share dispatcher so flipping
      them together is different from flipping them separately.
  (b) Should activation happen BEFORE Round 2B, BETWEEN Rounds 2 and 3,
      or AFTER Round 3?
  (c) For (ii), is the "gated-shadow" log tag sufficient? What
      additional instrumentation must accompany it so the hardcode is
      visible when the wiring event occurs?

Apply P4 (synthesis qualifier) if you propose a composite sequence.

### Q2. Verdict combination rule (apply P4 synthesis qualifier)

Three candidate rules proposed in Round 1:

  (alpha) First-definitive with contradiction veto. Walk the per-domain
          ordered tool list; first DEFINITIVE verdict wins; contradicting
          DEFINITIVE from another tool in the same dispatch vetoes and
          escalates. (Codex, ChatGPT.)

  (beta)  Confidence-weighted aggregation with contradiction veto.
          Aggregate all verdicts by confidence; contradiction across
          high-confidence verdicts vetoes and escalates. (Opus, DeepSeek.)

  (gamma) Composite: within-tier confidence-weighted, across-tier
          first-definitive, contradiction veto at any tier. (CC1's
          Round 1 synthesis proposal.)

Apply P4: does (gamma) produce a DEMONSTRABLY BETTER outcome than the
best of (alpha) or (beta) on a concrete case? Show the case, or choose
the most robust/flexible of (alpha) and (beta) with reasons.

### Q3. Novelty-vs-hallucination boundary

Can Stage 6 provide a theoretical UPPER BOUND on the boundary (not the
exact boundary)? If yes, state it with derivation. If no, state why
empirical fit from Bench Run 2 is the only path and what data would be
required.

Note: Gemini in Round 1 proposed nu_k <= 1 - R_k under strong
independence assumptions, self-marked [SPECULATIVE]. Does this upper
bound survive scrutiny, or not?

### Q4. Compelled-convergence instrumentation

Given Round 2B requires yield-or-refute with reasons, what additional
fields must the runner log to distinguish REASONED YIELD from COMPLIANCE
YIELD (i.e., yielding merely to satisfy the convergence instruction)?

Apply P4 if you propose more than one instrumentation scheme.

### Q5. Runner v1 preservation — what must Exp 40 log?

Under P2 (v1 preservation), what additional empirical properties beyond
the existing live-instrumented convergence should Exp 40 log to support
or falsify the preservation case for Exp 41-53? Name specific log
fields and acceptance criteria.

### Q6. Exp 40 runner topology

Round 1 endorsed star-with-paired-challenge (4/5) as a variant for
Exp 41+. For the Exp 40 run itself (single-target: bench/dm/_feedback.py),
which of these is correct, with reasons:

  (a) Keep star for Exp 40; introduce paired-challenge at Exp 41.
  (b) Introduce star-with-paired-challenge for Exp 40 (generates
      experimental evidence on the topology itself at the earliest
      point).
  (c) Run star in Exp 40 and star-with-paired-challenge in Exp 41, then
      compare.

Apply P4 if you propose a composite.
"""

# ---------------------------------------------------------------------------
# Final charge (how to answer)
# ---------------------------------------------------------------------------

CHARGE = r"""
## Final charge

Answer the six questions. Each answer must contain:

  1. A SINGLE DEFINITIVE position on the question.
  2. Full workings (reasoning chain or tool output).
  3. A P-pass: state what could falsify your answer.

Applicable transformations:
  - Where Stage 6 math admits a quantitative answer, give the
    quantitative answer (no qualitative opt-out).
  - Where P4 (synthesis qualifier) applies, either demonstrate the
    synthesis's superiority on a concrete case or pick the most
    robust/flexible single position.
  - State explicitly which position you adopt; do not produce a menu
    for the founder to choose from.

Word budget: up to 3,000 words across the six answers.
"""

# ---------------------------------------------------------------------------
# Prompt builder
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
# Exp 40 Pre-launch Panel Review — Round 2A of 3

You ({self_display}) are one of five frontier models. Four other models
receive the identical prompt in parallel. Your answers will be shown to
the other models in Round 2B, which requires yield-with-reasons or
refute-with-reasons on each divergent point.

Protocol: CDSFL + FFAFP, Stage 6 math as mathematical arbiter. Formal
conclusions in prose. No qualitative opt-out.

---

{STAGE6_MATH}

---

{FFAFP}

---

{CONVERGENCE}

---

{STANDING_POLICY}

---

{ROUND1_SUMMARY}

---

{QUESTIONS}

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
    print("  EXP 40 PRE-LAUNCH PANEL REVIEW — Round 2A of 3")
    print(f"  Timestamp: {ts}")
    print("  Protocol: CDSFL + FFAFP, Stage 6 math as arbiter")
    print("  New in Round 2: compelled convergence, no qualitative opt-out,")
    print("                  four standing policies (shadow-promotion-now,")
    print("                  runner v1 preservation, 15 experiments,")
    print("                  synthesis qualifier)")
    print("  Models: ge, cx, cc2, cgpt, ds (parallel, star dispatch)")
    print("  Charge: six questions (Q1-Q6), single definitive answer each")
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
