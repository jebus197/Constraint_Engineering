#!/usr/bin/env python3
"""Composer Review Confer: 5-model CDSFL review of the built composer.

Tight box: models MUST propose specific code fixes. No critique without solution.
Max 2 rounds — this is refinement, not exploration.
"""

import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from experiment_11_orchestrator import (
    call_openrouter, call_gemini, call_deepseek, call_codex, _log,
)

CDSFL_FORMAL_PATH = Path(__file__).parent / "directives" / "universal" / "cdsfl_core_formal.md"
CDSFL_FORMAL = CDSFL_FORMAL_PATH.read_text(encoding="utf-8") if CDSFL_FORMAL_PATH.exists() else ""

COMPOSER_CODE = (Path(__file__).parent / "cdsfl_registry" / "composer.py").read_text(encoding="utf-8")

OUTPUT_DIR = Path(__file__).parent / "logs" / "composer_review_confer"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CONFER_PROMPT = f"""
=== MANDATORY OPERATING CONSTRAINT — READ THIS FIRST ===

You have SIX problems to solve. You MUST provide a concrete, implementable
solution for EACH ONE. This is not optional. There is no "skip" option. There
is no "needs further research" option. There is no "CONVERGED" option. There
is no "NO FIXES" option.

Your output terminates ONLY when all six problems have a solution.

For each problem, your output format is:

PROBLEM N SOLUTION:
CODE: [the exact Python code that solves it — complete function or class, not a sketch]
INTEGRATION: [where this code goes — file, function, line number]
TEST: [one concrete assertion that proves it works]

If your solution for one problem depends on another, state the dependency.

You are forbidden from:
- Restating the problem without solving it
- Saying a problem needs empirical data before it can be solved
- Proposing that someone else solve it later
- Critiquing the architecture instead of fixing it
- Producing any output that is not a solution to one of the six problems

You are inside the problem box. The only way out is six solutions.

=== END MANDATORY CONSTRAINT ===

=== THE CODE ({len(COMPOSER_CODE)} chars) ===

{COMPOSER_CODE}

=== THE SIX PROBLEMS YOU MUST SOLVE ===

PROBLEM 1: UNIVERSAL PACKET TOO LARGE FOR SMALL-CONTEXT MODELS
The universal directive (cdsfl_core_formal.md) is 9,597 chars. DeepSeek's
phenotype cap is 4,000 chars. The universal is HARD and cannot be deleted.
But it CAN be re-rendered in a minimal format that preserves every HARD
constraint in fewer characters. Write the function that does this. The
minimal rendering must contain every constraint from universal.toml and
every HARD behavioural directive, but strips all explanatory prose,
examples, markdown formatting, and duplicate statements.

PROBLEM 2: PRUNING IS TOO COARSE
Currently pruning removes entire packets. If a domain packet has 10
directives and only 2 need to go, all 10 are lost. Write a function that
does intra-packet pruning: given a packet and a character budget, remove
individual SOFT directives (identified by section breaks or numbered items)
while preserving all HARD directives within the packet.

PROBLEM 3: PHENOTYPE TRANSFORM IS TOO BASIC
The current transform strips examples and caps length. For models like
DeepSeek that need minimal prompts, this is insufficient. Write an
improved _apply_phenotype_transform that also: (a) removes markdown
section headers and replaces with plain text labels, (b) collapses
multi-line directives to single-line where possible, (c) deduplicates
directives that say the same thing in different words within the same
packet. Provide the complete replacement function.

PROBLEM 4: NO PHENOTYPE x DOMAIN INTERACTION HANDLING
When a domain directive says "provide detailed mathematical proofs" and a
phenotype says "use minimal format", they conflict. Write the interaction
resolver: a function that takes a composed directive set and resolves
conflicts between layers by applying the rule: HARD always wins; for
SOFT conflicts, higher layer (universal > domain > phenotype) wins; for
same-layer conflicts, more specific (domain > general) wins. Output the
resolved set with conflicts logged.

PROBLEM 5: COHERENCE BUDGET THRESHOLDS ARE UNGROUNDED
The current thresholds (0.01 to 0.02) are guesses. We have data from
Experiments 12-17: per-model response quality, finding counts, token
usage, and directive lengths. Write a calibration function that takes
experiment log data (JSON files with model, chars, elapsed_s, response
fields) and computes the optimal coherence threshold per model as the
density value above which finding quality (findings per 1000 tokens)
drops by more than 10% from peak.

PROBLEM 6: COMPOSER NOT WIRED INTO ORCHESTRATOR
The composer exists but nothing calls it. Write the integration code:
the specific changes to experiment_11_orchestrator.py that replace the
current static directive loading with composer.compose() calls. Show
the exact functions that change, the exact import statements, and the
exact call sites. The orchestrator file is at:
bench/experiment_11_orchestrator.py
The dispatch function is at line ~540 (dispatch_to_model).
The directive loading currently happens via config.system_prompt_path.

=== CONTEXT: WHAT THE COMPOSER DOES ===
Assembles per-dispatch directive sets from four layers:
1. Universal (HARD, never pruned, never transformed)
2. Domain (SOFT, selected by task domain, phenotype-transformed)
3. Phenotype (transform operator — modifies HOW directives render per model)
4. Situation (SOFT, per-dispatch confer packet)

Key features: monotonicity enforcement, coherence budgeting, SOFT pruning,
phenotype-as-transform, composition identity hash (CID), manifest logging.

=== TEST OUTPUT FROM CURRENT COMPOSER ===
- opus_4_6:     12035 chars, density 0.0060, budget 0.020 — WITHIN
- codex_5_3:     6035 chars, density 0.0126, budget 0.012 — MARGINAL OVER
- chatgpt_5_4:   8035 chars, density 0.0095, budget 0.015 — WITHIN
- gemini_3_1_pro: 8035 chars, density 0.0095, budget 0.015 — WITHIN
- deepseek_v3:   4035 chars, density 0.0188, budget 0.010 — OVER

Solve all six. No escape. No debate. Solutions only.
"""

MODELS = [
    ("CC2", "anthropic/claude-opus-4-6", "openrouter"),
    ("CX", None, "codex_exec"),
    ("ChatGPT", "openai/gpt-5.4", "openrouter"),
    ("Gemini", "gemini-3.1-pro-preview", "google"),
    ("DeepSeek", "deepseek-reasoner", "deepseek"),
]


def dispatch(label, model_id, api, prompt, round_idx):
    """Dispatch to a model and save results."""
    _log(f"  Dispatching to {label} ({model_id or 'codex exec'}) via {api}...")
    t0 = time.monotonic()
    try:
        if api == "openrouter":
            text = call_openrouter(model_id, CDSFL_FORMAL, prompt, max_tokens=32768, timeout=300)
        elif api == "codex_exec":
            text = call_codex(prompt, CDSFL_FORMAL, timeout=600, max_retries=1)
        elif api == "google":
            text = call_gemini(model_id, CDSFL_FORMAL, prompt, max_tokens=32768, timeout=300)
        elif api == "deepseek":
            text = call_deepseek(model_id, CDSFL_FORMAL, prompt, max_tokens=16384, timeout=900)
        else:
            raise ValueError(f"Unknown API: {api}")
        elapsed = time.monotonic() - t0
        _log(f"  {label}: {len(text)} chars, {elapsed:.1f}s")

        ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        outfile = OUTPUT_DIR / f"round{round_idx}_{label.lower()}_{ts}.json"
        outfile.write_text(json.dumps({
            "model": label,
            "model_id": model_id or "codex-exec/gpt-5.4",
            "api": api,
            "round": round_idx,
            "chars": len(text),
            "elapsed_s": round(elapsed, 1),
            "response": text,
        }, indent=2), encoding="utf-8")
        _log(f"  Saved: {outfile}")
        return text, elapsed
    except Exception as e:
        elapsed = time.monotonic() - t0
        _log(f"  {label}: ERROR — {e} ({elapsed:.1f}s)")
        return f"ERROR: {e}", elapsed


def run_confer(max_rounds=2):
    """Run confer rounds. Max 2 — this is refinement."""
    all_findings = {}

    for round_idx in range(max_rounds):
        _log(f"\n=== CONFER ROUND {round_idx} ===\n")

        if round_idx == 0:
            prompt = CONFER_PROMPT
        else:
            prior = "\n\n".join(
                f"--- {label} (Round {round_idx - 1}) ---\n{text[:4000]}"
                for label, (text, _) in all_findings.get(round_idx - 1, {}).items()
            )
            prompt = (
                f"=== CONFER ROUND {round_idx} ===\n"
                f"Previous fixes proposed by all models:\n\n{prior}\n\n"
                f"Original code and constraints:\n{CONFER_PROMPT}\n\n"
                f"Your task: review prior fixes. For each:\n"
                f"- APPROVE: if the fix is correct and complete\n"
                f"- MODIFY: if the fix is right but needs adjustment (provide your version)\n"
                f"- REJECT: if the fix would break something (explain what breaks and provide alternative)\n"
                f"Then add any NEW fixes not yet proposed.\n"
                f"If all prior fixes are sound and you have nothing new, say CONVERGED.\n"
            )

        round_results = {}
        for label, model_id, api in MODELS:
            text, elapsed = dispatch(label, model_id, api, prompt, round_idx)
            round_results[label] = (text, elapsed)

        all_findings[round_idx] = round_results

        convergence_signals = sum(
            1 for label, (text, _) in round_results.items()
            if "CONVERGED" in text or "NO FIXES" in text
        )
        _log(f"\nRound {round_idx}: {convergence_signals}/5 models signal convergence")

        if convergence_signals >= 3:
            _log(f"Convergence reached at round {round_idx}.")
            break

    _log(f"\nConfer complete. {len(all_findings)} rounds, results in {OUTPUT_DIR}")


if __name__ == "__main__":
    _log("Composer Review Confer — 5 models under CDSFL (tight box)")
    _log(f"Output: {{OUTPUT_DIR}}")
    run_confer(max_rounds=2)
