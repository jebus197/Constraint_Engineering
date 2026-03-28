# Experiment 12: Live Orchestration Validation

## Purpose

First live test of the dynamic management layer (`dynamic_management.py`) under
real distributed compute conditions. The management layer produced by Experiment
11 (4-model converged formalisation, 3161 lines, 164 tests) has never been
exercised with actual model dispatch. This experiment validates it.

## What This Tests

1. **Pre-dispatch feasibility** — does the probabilistic capacity check prevent
   overwhelm before it happens (the Codex timeout scenario)?
2. **Adaptive task routing** — after the blind round, does the fingerprint update
   correctly characterise each model's strengths, and does the next round's
   allocation reflect those strengths?
3. **Convergence detection** — does kappa(r) correctly identify when the models
   have nothing new to add?
4. **Diminishing returns** — does mu(r) correctly signal when additional rounds
   aren't worth the cost?
5. **Real-time event stream** — does the PM receive events during dispatch and
   react appropriately?
6. **No model excluded for capability** — every model gets work matched to its
   demonstrated strengths. Adaptive routing, not benching.

## Task Domain

The test task must be substantial enough to generate real findings across multiple
rounds, but bounded enough that convergence is achievable. Candidate: P-pass the
dynamic management module itself — the schema eats its own tail. This provides a
natural stopping point (the module either has flaws or it doesn't) and makes
the experiment self-documenting.

Alternative: P-pass the Mathematical Appendix (already done in meta-test Stage 1,
but with the old orchestration — redoing it with the management layer active would
be a clean comparison).

## Architecture

```
CC1 (this session, Claude Opus 4.6)
  │
  ├── DynamicManager (dynamic_management.py)
  │     ├── RoleAssignment: assigns PM, COL, PAR from fingerprints
  │     ├── LoadBalancer: allocates tasks per model capability
  │     ├── RoundProgressionFSM: BLIND → ROUND_1 → ... → TERMINAL
  │     ├── ConvergenceDetector: kappa(r) → converged?
  │     ├── DiminishingReturnsDetector: mu(r) → stop?
  │     ├── FailureHandler: detect, recover, reallocate
  │     └── Live fingerprint update: observe → EMA → reallocate
  │
  ├── Experiment 11 Orchestrator (API dispatch layer)
  │     ├── call_openrouter() → CC2, ChatGPT
  │     ├── call_codex() → Codex
  │     ├── call_gemini() → Gemini
  │     └── call_deepseek() → DeepSeek
  │
  └── Event stream → CC1 observes all DynamicManager decisions
```

CC1 is the collator. CC1 does NOT make synthesis or stop decisions — the
DynamicManager does. CC1 executes the manager's decisions via the API layer
and feeds results back.

CC2 is assigned PM by the management layer (if its fingerprint scores highest).
CC2's synthesis capability is used via API calls, not special-cased.

## Phases

### Phase 0: Preflight
- Run preflight on all 5 models (identity + compliance)
- Initialise DynamicManager with model pool
- Check pre-dispatch feasibility for the task prompt

### Phase 1: Blind Round
- FSM state: BLIND
- Same prompt to all feasible models
- DynamicManager detects failures, computes initial fingerprints
- Transition: BLIND → ROUND_1

### Phase 2+: Distributed Rounds (adaptive)
- FSM state: ROUND_k
- DynamicManager allocates subtasks based on LIVE fingerprints
- PM (CC2 or whoever scores highest) synthesises round findings
- Fingerprints updated from observed output
- Convergence and diminishing returns checked
- Loop until TERMINAL (converged, diminished, max_rounds, or failure)

### Phase Final: Report
- Collect all round results, event log, fingerprint evolution
- Document what the management layer decided and why
- Compare against Experiment 11 (no management layer) if applicable

## Circuit Breaker (inherited from Experiment 11)

All 7 halt conditions from EXECUTION_PLAN_EXPERIMENT_11.md apply:
1. Auth failure on any API
2. Wrong model identity
3. CDSFL non-compliance
4. Empty response (after retry)
5. Budget exceeded ($20 cap)
6. Rate limit exhaustion
7. Data corruption

## Models

| Label | Model | API | Expected Role |
|-------|-------|-----|---------------|
| CC2 | Claude Opus 4.6 | OpenRouter | PM (if fingerprint highest) |
| Codex | GPT-5.4 | codex exec | PAR (600s timeout → feasibility check) |
| ChatGPT | GPT-5.4 | OpenRouter | COL or PAR |
| Gemini | 3.1 Pro | Google API | PAR |
| DeepSeek | V3.2 | DeepSeek API | PAR |

Roles determined by DynamicManager at runtime, not pre-assigned.

## Success Criteria

1. Management layer runs without crashes through at least 2 rounds
2. Feasibility check blocks dispatch to any model that would timeout
3. Fingerprints update from observed data (not just initial values)
4. Allocation shifts between rounds based on fingerprint changes
5. Convergence or diminishing returns triggers clean termination
6. Event log captures all management decisions with timestamps
7. No model excluded for capability — all active models get work

## Naming

**Experiment 12: Live Orchestration Validation** (internal)
**Live Wire Test** (shorthand)
