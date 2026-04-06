# Experiment 35 Plan — PolicyEngine Review with Capability-Aware Dispatch

Date: 6 April 2026
Status: DRAFT — awaiting Exp 34 completion and lessons learned

## Target

PolicyEngine: engine.py (15K) + schema.toml (12K).
Context: registry.py (14K).
Total artifact: ~54K chars (4.4x smaller than Exp 34's 235K).

## What Exp 35 Fixes Over Exp 34

### 1. Budget-Aware Prompt Builder

The star/blackboard runner currently builds one prompt for all models.
The insect brain's relay (line 196-292) already does per-model budget
sizing for findings. Exp 35 brings that same principle to the code
artifact and full prompt construction.

Implementation:
- _make_model_prompt(mc_label) consults CONTEXT_CHAR_BUDGET[mc_label]
- Budget tiers:
  - Full (Gemini 200K, ChatGPT 80K): target + schema + context + registry
  - Standard (Codex 60K): target + schema + registry (strip context if over)
  - Constrained (DeepSeek 30K, CC2 30K): target + schema only, context stripped,
    registry summary truncated to fit
  - Minimal (Haiku, future): focused question about specific function
- If target alone exceeds budget: deliver section assignment (see section map)
- The prompt explicitly states what scope the model is reviewing
- Findings go into the same global FindingRegistry regardless of scope

For Exp 35 specifically: the full artifact is ~54K chars. Even with prompt
overhead and registry growth, Gemini/ChatGPT/Codex have headroom. DeepSeek
at 30K budget gets target + schema (27K) without context — tight but viable.
CC2 at 30K gets the same, but CC2 dispatches via CLI which handles large
prompts through its own chunking.

### 2. Section Map for Large Targets

Before the experiment starts, parse the target file into logical sections
at top-level class and def boundaries. Store as:

    sections = [
        {"name": "PolicyEngine.__init__", "start": 45, "end": 112, "chars": 2800},
        {"name": "PolicyEngine.evaluate", "start": 113, "end": 195, "chars": 3400},
        ...
    ]

Budget-constrained models on large targets get assigned sections by
rotation or by least-reviewed. Not needed for Exp 35 (target fits in
all budgets) but built now so Exp 36 and future experiments use it
automatically.

### 3. ITC — Adaptive Recovery After Failure

Per-model, per-round quality check after dispatch:

Detection:
- Context overflow: 400-level API error mentioning token limit
- Empty output: 0 findings parsed from non-empty response
- Zero output: empty or refused response
- Repetition: >40% finding ID overlap with own prior round
- Parse failure: response received but 0 findings extracted

Classification:
- CAPABILITY_MISMATCH: context overflow, consistent empty output (structural)
- TRANSIENT_FAILURE: API timeout, rate limit, single empty round (retry)
- DEGRADATION: repetition, declining finding count (narrow scope)

Adaptation (applied to NEXT round, not current):
- CAPABILITY_MISMATCH: narrow prompt scope (strip context, then section assign)
- TRANSIENT_FAILURE: retry same prompt (max 1 retry per round)
- DEGRADATION: change focus area ("you have already found X, now review Y")

No model is removed from active_models. Every model works every round,
within its demonstrated capability.

### 4. Persistent Signed Fingerprints

After each experiment, write an observed capability profile per model:

    {
        "model_id": "DeepSeek",
        "experiment": "exp34_endocrine",
        "timestamp": "2026-04-06T01:15:00+01:00",
        "observed": {
            "max_successful_context_chars": 28500,
            "max_failed_context_chars": 225000,
            "failure_modes": ["context_overflow"],
            "task_completion_rate": 0.65,
            "avg_findings_per_round": 2.1,
            "best_scope": "target_only"
        }
    }

Storage: bench/fingerprints/<model_id>.json
Signing: Merkle inclusion proof via verification_chain.py (already built).
The fingerprint is appended to the verification chain as a sealed record.
Ed25519 signature optional but available.

On experiment start: load fingerprints, merge with INITIAL_FINGERPRINTS.
Observed data takes precedence over static defaults. Right-size tasks
from R0. No discovery phase.

### 5. Immune Pipeline Activation

The Exp 34 runner already runs with observation_only=False (brain default).
Exp 35 continues this. Additionally:

- Rename *_v2_shadow() functions: drop _shadow suffix, update docstrings
- Typed LLM Classifier: rewire from disabled OpenRouter path to
  call_claude_cli with Haiku model ID (zero cost on Max plan)
- Review Exp 34 shadow log data for v1/v2 agreement before activating
  any cell that currently defers to v1

### 6. Bug Fixes Carried Forward

All 3 bugs fixed during Exp 34 are already applied to run_exp35:
- compose_for_model(): correct call signature with task_domain + situation
- DecomposedChunk(): content= not text=, no is_context
- decomposed_dispatch(): api/model_id/system_prompt, not mc=

### 7. Composer and Docstring Cleanup

- CC2 docstring: "via Claude CLI, Max plan" (not OpenRouter)
- Stale "Exp 33" references in log messages: correct to Exp 35
- SUPERSEDES removed from prompts (already done in confer fixes)

## Architecture Summary

    R0: Load signed fingerprints -> right-size all prompts from start

    Each round:
      1. Budget-aware prompt builder sizes per model
      2. Dispatch (single-turn if right-sized, decomposed only if needed)
      3. Parse findings -> FindingRegistry
      4. ITC check: detect failure, classify, adapt next round
      5. Immune pipeline (observation_only=False)
      6. Convergence gate evaluation
      7. Update observed fingerprints (in memory, persist at end)

    Experiment end:
      1. Seal fingerprints to verification chain
      2. Write updated fingerprint files
      3. Standard report + TTS

## Dependencies

- Exp 34 completion: lessons learned fold into this plan
- Shadow log review: v1/v2 agreement data for immune activation decision
- Haiku model ID verification: confirm CLI dispatch works for Haiku

## Constraints

HARD: No model benched. Every model works every round.
HARD: Prompts never exceed demonstrated capability (signed fingerprint).
HARD: Star/blackboard topology retained (canonical state ownership).
HARD: FindingRegistry is the single source of truth for all models.
SOFT: Section map built even if not needed for Exp 35 artifact size.
SOFT: Fingerprint signing via Merkle (could defer to Ed25519 later).

## Estimated Implementation

- Budget-aware prompt builder: ~40 lines in runner
- Section map parser: ~25 lines (utility, reusable)
- ITC detection + classification + adaptation: ~60 lines in runner
- Persistent fingerprints (write + load + merge): ~50 lines (new module)
- Fingerprint signing (Merkle integration): ~20 lines
- Immune pipeline rename + LLM classifier rewire: ~30 lines in immune_agents.py
- Total: ~225 lines of new/modified code

## Open Questions (to resolve from Exp 34 observation)

1. Does DeepSeek produce useful findings when given target-only (no context)?
2. What is the actual registry summary growth rate per round?
3. Do models produce structured verdicts with the fixed composer?
4. What is the v1/v2 immune pipeline agreement rate under real data?
5. Any other failure modes not yet observed?
