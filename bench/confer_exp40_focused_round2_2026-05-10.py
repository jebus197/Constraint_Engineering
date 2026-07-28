#!/usr/bin/env python3
"""
Exp 40 Pre-Launch — Focused Confer Round 2 (10 May 2026)
=========================================================

A single-round compelled-convergence panel review of the items not
covered by Round 1 (consolidated-plan panel review, 2026-04-21):

- Q1. G2 code-correctness fix at bench/immune_agents.py:5411-5421
      (claim_id/severity → finding_id/confidence dict-comp key rename).
- Q2. Section 2a target-article scope briefs for Exp 47, 51, 52, 53
      (synthesised native modules: biology, physics, chemistry,
      engineering — 4-5 falsifiable claim clusters per module).
- Q3. Section 6b trigger specifications for G6, G7, G8
      (specialist-to-specialist verdict-conflict resolution; MERGE
      deadlock auto-arbitration; burst-mode Phase 0 convergence
      override).
- Q4. (Optional) Trigger-vs-implement policy for G6, G7, G8.
- Q5. Closure-now framing for the four residuals identified in the
      22 April 2026 founder oversight Q&A. Founder's reasoning for
      closure-now (rather than defer): both founder and agent are
      context-bounded; deferral has produced observable cost
      (16-day hiatus surfaced exactly the loss-of-thread the residuals
      were guarding against). Panel asked to ratify or refute this
      framing on the merits, not reflexively recommend defer.

Round-1 prior framing remains valid; this round does NOT relitigate it.

Models (panel rotation 2026-05-10, smoke-tested 2026-05-10):
    Gemini 3.1 Pro Preview — google/gemini-3.1-pro-preview via OpenRouter
    Codex GPT-5.5          — openai/gpt-5.5 via OpenRouter
    CC2 Claude Opus 4.7    — opus via Claude CLI piped mode
    ChatGPT GPT-5.5        — openai/gpt-5.5 via OpenRouter
    DeepSeek V4 Pro        — deepseek-v4-pro via DeepSeek direct API

Dispatch: parallel via ThreadPoolExecutor(max_workers=5), star topology
          (each model talks only to CC1; no cross-model leakage).
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
    call_deepseek,
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

LOGS_DIR = REPO_ROOT / "bench" / "logs" / "confer_exp40_focused_round2_2026-05-10"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Updated panel (2026-05-10): all rotated to current frontier where a
# successor exists; Gemini route moved to OpenRouter for credit
# economics; DeepSeek upgraded R1-0528 → V4 Pro on direct API since the
# older endpoint is no longer listed.
MODELS = [
    ("gemini",   "google/gemini-3.1-pro-preview", "openrouter"),
    ("codex",    "openai/gpt-5.5",                "openrouter"),
    ("cc2",      "opus",                          "claude_cli"),
    ("chatgpt",  "openai/gpt-5.5",                "openrouter"),
    ("deepseek", "deepseek-v4-pro",               "deepseek"),
]

# ---------------------------------------------------------------------------
# CDSFL system prompt
# ---------------------------------------------------------------------------

CDSFL_PATH = REPO_ROOT / "bench" / "directives" / "universal" / "cdsfl_core_formal.md"
CDSFL_TEXT = CDSFL_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# Consolidated plan (full content injected as background)
# ---------------------------------------------------------------------------

PLAN_PATH = REPO_ROOT / "experimental_notes" / "Exp40_to_54_Consolidated_Plan_2026-04-21.md"
PLAN_TEXT = PLAN_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# Round-2 framing (load-bearing — read first)
# ---------------------------------------------------------------------------

ROUND2_FRAMING = r"""
## Round 2 framing (load-bearing)

This is a focused follow-up to the Round 1 consolidated-plan panel
review of 21 April 2026. Round 1 covered F1/F2/F3 strategy, Gate C
preflight step, Stage 6 design, Exp 40-54 scope and ordering, RQ6b
native-synthesis commitment, K/L/M non-distortion principle, and the
shadow-promotion-now policy. Those items are NOT relitigated here.

Round 2 covers items not yet panel-reviewed:

1. The G2 code-correctness fix at bench/immune_agents.py:5411-5421.
2. Section 2a target-article scope briefs (Exp 47, 51, 52, 53).
3. Section 6b trigger specifications for G6, G7, G8.
4. Trigger-vs-implement policy for G6, G7, G8 (optional).
5. The closure-now disposition of four residuals identified in the
   22 April 2026 founder oversight Q&A.

Anchors that remain in force from Round 1:

- bench/exp40_configs/40_gate.json acceptance criterion: "gamma >= 0.30
  OR (3 consecutive rounds with 0 novel CRITICAL findings). Gamma-alt
  implemented in reference_runner_v2._check_gamma_alt_convergence."

- Stage 6 orthogonality (canonical model). R_k = VALIDITY,
  nu_k = NOVELTY, c_ext = SEARCH QUALITY. The three are independent
  reporting dimensions and MUST NEVER be collapsed into a single
  score before reporting.

- The "v1 preservation" framing remains refuted; do not reuse it.

Compelled-convergence rules:
- Do NOT offer a menu of alternatives per question. Offer one answer.
- If a question is malformed under correct framing, say so in one
  sentence and answer the closest well-formed question.
- Word budget: 2400 words total across Q1-Q5.
"""

# ---------------------------------------------------------------------------
# Q1 supporting material — G2 code excerpt
# ---------------------------------------------------------------------------

G2_EXCERPT = r"""
## Supporting material for Q1 — G2 code change

Pre-fix (21 April enrichment) at bench/immune_agents.py around line
5411 contained dict-comprehension keys that were not CellVerdict
fields:

    shadow_detail = {
        "claim_id":     getattr(v, "claim_id",   None),  # NOT a field
        "verdict":      getattr(v, "verdict",    None),
        "severity":     getattr(v, "severity",   None),  # NOT a field
        "tool_used":    getattr(v, "tool_used",  None),
        "evidence":     (getattr(v, "evidence",  "") or "")[:256],
    }

dataclasses.fields(CellVerdict) returns exactly:
    {finding_id, verdict, confidence, tool_used, evidence}

claim_id and severity therefore resolved to None on every record,
halving the Round 2 RQ4 non-distortion-measurement signal.

Post-fix (22 April 2026, commit 991cde0) at the same location:

    shadow_detail = {
        "finding_id":   getattr(v, "finding_id", None),  # real field
        "verdict":      getattr(v, "verdict",    None),
        "confidence":   getattr(v, "confidence", None),  # real field
        "tool_used":    getattr(v, "tool_used",  None),
        "evidence":     (getattr(v, "evidence",  "") or "")[:256],
    }

Regression test bench/tests/test_shadow_audit_klm.py (11 tests, AST
schema check + field binding via dataclasses.fields(CellVerdict) +
behavioural replica + log-format pin) all passing in 2.48 s.

Live evidence: bench/logs/immune_pipeline.log at 02:05:51 BST
2026-04-22 shows the rename emitting under live load:
    detail=[{"finding_id": "sf1", "verdict": "CONFIRMED",
             "confidence": 0.85, "tool_used": "rdkit", ...}]
"""

# ---------------------------------------------------------------------------
# Residuals context for Q5
# ---------------------------------------------------------------------------

RESIDUALS_CONTEXT = r"""
## Supporting material for Q5 — Four residuals and their disposition

Four residuals were identified in the 22 April 2026 founder oversight
Q&A and have been closed on 10 May 2026 under a founder directive that
explicitly rejected deferral. The directive's reasoning, in the
founder's own words: "Context is king, and while you are context
limited and may 'forget' to address these issues later, my hiatus has
proved I am also subject to similar context loss and the potential to
forget, so you should take whatever action may be required to resolve
them now."

The four residuals as closed:

(a) Exp 39-0 gate state cross-check.
    Memory file claimed COMPLETE; live log records status INCOMPLETE
    (6 rounds, no convergence, final kappa 0.619, 111 findings).
    Resolution: cross-check confirmed Exp 39-0 was a CALIBRATION
    experiment that surfaced finding F7/F23 — the
    max_open_crit_high=0 threshold was structurally unreachable. Fix
    landed: default raised 0 → 5 at
    bench/reference_runner_v2.py:259 (mirrored at
    reference_runner.py:207), regression-pinned at
    bench/tests/test_runner_status_transitions.py:242. The original
    threshold was the SUBJECT of Exp 39-0, not its prerequisite.
    ce_state.md updated to reflect this distinction.

(b) Per-finding R_k time-series tracking — assessment.
    Resolution: not a blocker for any Exp 40-54 experiment as
    currently planned. Runner currently logs only latest R_k per
    finding; no plan-level requirement for per-round trajectory
    appears in the consolidated plan or MATHEMATICAL_APPENDIX.md.
    Forward-going enhancement candidate; no current dependency.

(c) Scientific-notation sub-rule amendment to locked note standard.
    Resolution: cdsfl_note_standard_v1.1.md created on 10 May 2026 as
    additive amendment, adding Rule 11 — 11a scientific-notation
    format `1×10^N (number-words)` with verified exponent-to-word
    correspondence; 11b `<digit>E.<digit>` item-reference recognition
    rule (prevents 1E.10 → "ten billion" misreading). All ten v1
    rules remain in force unchanged.

(d) Full retroactive F4 closure-state labelling sweep.
    Resolution: a Component Closure-State Index added to
    resources/ONBOARDING.md as a subsection of the F4 lexicon block,
    listing 19 running components with their labels (live_operational,
    shadow_integrated, library_complete), file locations, dates of
    state confirmation, and flip triggers where applicable.

The panel is asked: are these resolutions correct on the merits, or
does any of them require revision? The founder is explicitly NOT
asking the panel to recommend deferral on the basis that the residuals
"could have waited" — that question has been adjudicated.
"""

# ---------------------------------------------------------------------------
# Five questions
# ---------------------------------------------------------------------------

QUESTIONS = r"""
## Round 2 questions (Q1-Q5)

### Q1. G2 code-correctness fix

The fix at bench/immune_agents.py:5411-5421 renames dict-comp keys
from claim_id/severity to finding_id/confidence (the real CellVerdict
fields per dataclasses.fields(CellVerdict)). See "Supporting material
for Q1" above for pre-fix and post-fix excerpts, regression coverage,
and live-load evidence.

Is the fix correct on the merits — does it restore the intended
non-distortion-measurement signal that the K/L/M shadow audit was
designed to produce? Are the regression pins (AST schema check +
field-binding test + behavioural replica + log-format pin) sufficient
to prevent recurrence? Is there any latent issue at this code site
that the fix exposes or fails to address?

### Q2. Section 2a target-article scope briefs

Section 2a of the consolidated plan defines scope briefs for the four
synthesised native modules:

- Exp 47 biology (4-5 claim clusters: sequence-validity, dimensional,
  statistical-distribution, mathematical, plus mandatory false-claim).
- Exp 51 physics (kinematics, conservation laws, dimensional
  consistency, special-function, plus mandatory false-claim).
- Exp 52 chemistry (SMILES validity, stoichiometry, molecular weight,
  functional-group identification, plus mandatory false-claim).
- Exp 53 engineering (load-factor, material-tolerance, safety-factor,
  dimensional consistency, plus mandatory false-claim).

For each module:
- Are the claim clusters sufficient to exercise the routed specialist
  tools at the experiment's intended depth?
- Is the per-cluster falsifiability route correctly named (e.g.
  rdkit + collections.Counter for stoichiometry)?
- Is 15-25K characters per module the right size, or should it grow
  or shrink given the cluster count?
- Is there a missing claim cluster that the experiment will need but
  the brief omits?

### Q3. Section 6b trigger specifications for G6, G7, G8

Section 6b of the consolidated plan specifies entry triggers,
multi-tool pairings, and minimum evidence thresholds for the three
deferred gaps:

- G6. Specialist-to-specialist verdict-conflict resolution. Trigger:
  Exp 44 post-mortem; migration to Exp 49 if Exp 44 is clean.
- G7. MERGE deadlock auto-arbitration. Trigger: Exp 44 post-mortem;
  migration to Exp 49 if clean.
- G8. Burst-mode Phase 0 convergence override. Trigger: external
  authorisation (out-of-arc).

For each:
- Is the entry trigger correctly identified and scoped?
- Is the multi-tool pairing on activation (pytest + AST + inspect +
  trace-log parsing) sufficient to validate the resulting code?
- Is the minimum evidence threshold (specific failure mode observed in
  post-mortem logs at counts >= some threshold) the right shape, or
  should the thresholds be more or less stringent?

### Q4. Trigger-vs-implement policy for G6, G7, G8 (optional)

The current policy is: trigger-and-wait — specifications written now,
implementation deferred until post-mortem evidence justifies the
specific arbitration rule. This is Popperian discipline: arbitration
rules emerge from observed conflicts rather than being pre-registered.

Is trigger-and-wait the right policy for all three (G6, G7, G8), or
is one of them better implemented now? Specifically:
- G6 and G7 are concurrency/protocol resolutions — does observation
  add information that pre-registration cannot?
- G8 is a burst-mode override; out-of-arc anyway, but is the trigger
  correctly identified as "external authorisation"?

This question is OPTIONAL — answer only if you have a substantive
view distinct from Q3.

### Q5. Closure-now disposition of four residuals

The four residuals (a, b, c, d) and their closures-as-applied-on-10-May
appear in "Supporting material for Q5" above. The founder explicitly
rejected deferral. Panel is asked to evaluate the closures on the
merits:

- (a) Is the cross-check correct — was the original max_open_crit_high=0
  the SUBJECT of Exp 39-0 rather than its prerequisite? Should ce_state.md
  reflect anything else about Exp 39-0's actual state?
- (b) Is the assessment correct — does any experiment in the Exp 40-54
  arc require per-finding R_k time-series tracking? Examine the
  consolidated plan for any latent dependency that the assessment
  might miss.
- (c) Is the v1.1 amendment correctly scoped and worded — does Rule 11
  (11a + 11b) close the scientific-notation gap without introducing a
  new ambiguity?
- (d) Is the Component Closure-State Index a sufficient closure of the
  retroactive labelling sweep, or should specific component labels be
  challenged as wrong? In particular, is F3 DEBUG_CHANNEL_CHECK
  correctly labelled library_complete (as opposed to shadow_integrated
  given that it runs in dev/CI), and are the K/L/M shadow-audit and
  Stage 6 calibrator labels (shadow_integrated) correct?

The panel is NOT asked to recommend deferral on any of (a)-(d). That
question is adjudicated. The panel IS asked to find what is wrong,
incomplete, or worth strengthening in the resolutions as applied.
"""

# ---------------------------------------------------------------------------
# Response format
# ---------------------------------------------------------------------------

RESPONSE_FORMAT = r"""
## Response format (compelled-convergence)

For each question Q1-Q5 (Q4 optional):

1. FFAFP workings (Find, Follow, Analyse, Fix, P-pass). Keep short.
2. One final definitive position, bolded as `**Final position:** ...`.
3. Where a code claim, anchor to the file:line cited above; where a
   plan-content claim, anchor to the section number in the
   consolidated plan; where a residuals claim, anchor to the
   resolution as stated in "Supporting material for Q5".

Compelled-convergence reminder:
- One answer per question, not a menu.
- If you believe a question is malformed, say so in one sentence and
  answer the closest well-formed question.
- Word budget: 2400 words total.

Target: panel converges on a single position per question.
"""


# ---------------------------------------------------------------------------
# Compose full user prompt
# ---------------------------------------------------------------------------

def build_user_prompt() -> str:
    return (
        ROUND2_FRAMING
        + "\n\n"
        + G2_EXCERPT
        + "\n\n"
        + RESIDUALS_CONTEXT
        + "\n\n"
        + "## Background — Exp 40-54 consolidated plan (full text, for cross-reference)\n\n"
        + PLAN_TEXT
        + "\n\n"
        + QUESTIONS
        + "\n\n"
        + RESPONSE_FORMAT
    )


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

def _dispatch(model_label: str, model_id: str, api: str,
              system_prompt: str, user_prompt: str) -> dict:
    start = time.time()
    try:
        if api == "claude_cli":
            response = call_claude_cli(model_id, system_prompt, user_prompt)
        elif api == "openrouter":
            response = call_openrouter(model_id, system_prompt, user_prompt)
        elif api == "deepseek":
            response = call_deepseek(model_id, system_prompt, user_prompt)
        else:
            raise ValueError(f"Unknown api: {api}")
        elapsed = time.time() - start
        return {
            "model": model_id,
            "label": model_label,
            "api": api,
            "response": response,
            "time_s": round(elapsed, 1),
            "chars": len(response) if response else 0,
            "prompt_chars": len(system_prompt) + len(user_prompt),
        }
    except Exception as e:
        elapsed = time.time() - start
        return {
            "model": model_id,
            "label": model_label,
            "api": api,
            "error": f"{type(e).__name__}: {e}",
            "time_s": round(elapsed, 1),
            "prompt_chars": len(system_prompt) + len(user_prompt),
        }


def main() -> int:
    system_prompt = CDSFL_TEXT
    user_prompt = build_user_prompt()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    total_chars = len(system_prompt) + len(user_prompt)
    print(f"Dispatching Exp 40 focused Round 2 to {len(MODELS)} models")
    print(f"Prompt size: {total_chars} chars "
          f"(system {len(system_prompt)} + user {len(user_prompt)})")
    print(f"Plan under reference: {PLAN_PATH.name} ({len(PLAN_TEXT)} chars)")
    print(f"Timestamp: {timestamp}")
    print(f"Logs: {LOGS_DIR}")
    print()

    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        futures = {
            ex.submit(_dispatch, label, mid, api, system_prompt, user_prompt): label
            for (label, mid, api) in MODELS
        }
        for fut in concurrent.futures.as_completed(futures):
            label = futures[fut]
            result = fut.result()
            results[label] = result
            if "error" in result:
                print(f"  {label}: ERROR in {result['time_s']}s — {result['error'][:200]}")
            else:
                print(f"  {label}: {result['chars']} chars in {result['time_s']}s")

            per_model_path = LOGS_DIR / f"{label}_{timestamp}.json"
            per_model_path.write_text(json.dumps(result, indent=2))

    combined_path = LOGS_DIR / f"combined_{timestamp}.json"
    combined_path.write_text(json.dumps(results, indent=2))
    print()
    print(f"Combined log: {combined_path}")

    errors = [label for label, r in results.items() if "error" in r]
    if errors:
        print(f"\n{len(errors)}/{len(MODELS)} models errored: {', '.join(errors)}")
        return 1
    print(f"\nAll {len(MODELS)} models returned cleanly.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
