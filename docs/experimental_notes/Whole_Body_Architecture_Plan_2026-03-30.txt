# Whole Body Architecture: Conversational Multi-Agent Coordination for CDSFL Distributed Compute

**Design Note, 30 March 2026**

---

## 1. Problem Statement

The current CDSFL distributed compute runner (`run_exp17_immune.py` and its predecessors) treats model dispatch as stateless batch RPC. Each round, all models receive the same accumulated findings and produce output in parallel. No model sees another model's output from the same round. No model can respond to, challenge, or validate a specific finding from a specific other model. The immune layer and load balancer operate around the models but never through them.

This produces three measurable deficits:

**(a) No within-round confer.** Models independently rediscover the same problems or produce contradictory findings that are never reconciled until a human reads them. The confer protocol (`c`) exists as a concept but is not implemented at the experiment level.

**(b) Attribution loss.** Findings are broadcast as anonymous lists. A model cannot say "CC2's finding IM_F003 is incorrect because..." because it does not know CC2 produced it. This prevents adversarial validation, the core mechanism of CDSFL.

**(c) No adaptive pacing.** Every model gets the same prompt at the same time regardless of capacity, health, or the state of other models. A struggling model cannot be told "wait, I will send you a smaller piece next" and a strong model cannot be told "Model B found X, verify it before proceeding."

Experiment 17 exposed these limitations operationally. Codex took 556 seconds on a 278K prompt while other models completed in 50–150 seconds. The decomposition fix (`pre_decompose_models`, task-level extraction, immune-driven auto-decomposition) addresses the symptom but not the architecture.

---

## 2. Proposed Architecture: The Whole Body

The metaphor is biological. The current system has organs (models) but no nervous system connecting them. The proposed architecture adds three communication layers.

### 2.1. Nervous System: Dispatch Sequencing

Replace parallel broadcast with sequential dispatch within each round. The `DynamicManager`'s role assignment (`player_manager`, `participant`) becomes operationally meaningful:

```
Round N, Task T:
  Step 1. Dispatch to Model A (strongest on this task per fingerprint).
  Step 2. Model A produces findings.
  Step 3. Dispatch to Model B with: "Model A found [findings]. Validate,
          challenge, or extend. Do not repeat."
  Step 4. Model B produces findings (including explicit responses to A).
  Step 5. Dispatch to Model C with A's and B's output.
  ...
  Step K. Player_manager (CC2) receives all output, arbitrates conflicts,
          produces final round synthesis.
```

The immune layer controls the sequence. If Model B times out at Step 4, the immune layer skips to Model C with A's findings only and records the gap. If Model A produces zero findings, the immune layer can insert a "recalibration prompt" before dispatching to B: "Model A found nothing. This may indicate the code is clean or that the prompt was insufficient. Apply deeper analysis."

### 2.2. Circulatory System: Attributed Finding Flow

Findings carry full provenance:

```
FINDING_ID: IM_R2_F003
SOURCE_MODEL: CC2
ROUND: 2
VALIDATED_BY: [Codex (Round 2, Step 4), Gemini (Round 2, Step 5)]
CHALLENGED_BY: []
STATUS: validated (2/5 independent confirmations)
```

Models see attributed findings. They can explicitly agree, disagree, or extend. The convergence detector uses attribution to measure genuine independent convergence (two models finding the same thing without seeing each other's output) versus echo (a model agreeing with a finding it was shown).

The `format_findings_for_context` function is extended:

```
FINDING_ID: IM_R2_F003 [CC2, validated by Codex + Gemini]
  SEVERITY: 0.88
  DESCRIPTION: DetectorHealthMonitor._verify_remediation_outcomes
  does not check whether the remediation was applied in the correct
  round...
  PROPOSED_FIX: Add round_idx comparison...
```

Models can now say: "CC2's IM_R2_F003 is correct but the proposed fix is incomplete because it does not account for the damping window."

### 2.3. Endocrine System: Adaptive Pacing Signals

The immune layer can send control signals to models as part of the prompt, not just task instructions:

```
SYSTEM_SIGNAL: PACE=STEP_BY_STEP
"Read and understand the code structure first. Acknowledge with a
brief summary of what you see. Do not produce findings yet."

SYSTEM_SIGNAL: PACE=CONTINUE
"You previously summarised the code structure as [summary]. Now
produce findings focused on [boundary]."

SYSTEM_SIGNAL: HOLD
"Do nothing now. More context will follow in the next dispatch.
This is Step 1 of a multi-step review sequence."

SYSTEM_SIGNAL: FOCUS_SHIFT
"Model A and Model B disagree on [finding]. Review both arguments
and adjudicate. Produce a VERDICT: AGREE_A, AGREE_B, or NEITHER
with evidence."
```

The load balancer determines which signals to send based on:
- Model capacity (`L`, `L_std`) relative to prompt size
- Observed latency history (`tau`, recent dispatch times)
- Finding quality metrics (abstraction index, severity distribution)
- Health state from immune layer (failure count, remediation history)

A model with high latency and declining finding quality gets `STEP_BY_STEP`. A model with spare capacity and strong prior output gets the full prompt with `CONTINUE`. A model that timed out last round gets a decomposed prompt with `HOLD` for the first step and `CONTINUE` for the second.

---

## 3. Implementation Plan

### Phase 1: Attributed Findings (minimal, backward-compatible)

Add `source_model` field to `Finding` dataclass. Already partially present via `finding_id` prefix, but make it explicit. Update `format_findings_for_context` to include attribution. Update `parse_findings` to preserve source. No change to dispatch pattern.

**Estimated effort:** 50 lines changed across 3 files. Can be done immediately after Experiment 17.

### Phase 2: Sequential Dispatch (within-round confer)

Replace the model loop in `_dispatch_round` with a sequenced pipeline:
- `DynamicManager.get_dispatch_order(task_key, round_idx)` returns an ordered list of models based on role, fingerprint, and health.
- Each model's prompt includes the previous models' findings from the same round (attributed).
- `player_manager` dispatches last and produces a synthesis.

The immune layer monitors the sequence and can skip, reorder, or insert recalibration prompts.

**Estimated effort:** 150 lines new in `run_exp17_immune.py`, 50 lines new in `dynamic_management.py` (dispatch ordering logic).

### Phase 3: Multi-Step Dispatch (pacing signals)

Add `SYSTEM_SIGNAL` protocol to prompt construction. The immune layer and load balancer jointly decide the pacing strategy per model per task. Models that support multi-turn (API-based: CC2, ChatGPT, Gemini) get true conversational dispatch. Models that are single-shot (`codex exec`) get the signal embedded in the prompt with explicit instructions.

This phase requires changes to `dispatch_to_model` to support multi-turn for API-based models. The multiprocessing watchdog extends to cover multi-step sequences.

**Estimated effort:** 200 lines new, significant refactor of dispatch layer.

### Phase 4: Closed-Loop Feedback (full whole body)

The immune layer monitors partial output during dispatch (where APIs support streaming). If a model's output shows signs of going off-track (repetition, declining novelty, hallucinated code references), the immune layer can:
- Terminate the dispatch early and record a partial result.
- Send a correction signal in the next step.
- Reallocate the task to another model.

This is the full nervous system: sensory input (streaming output monitoring), processing (immune layer diagnosis), motor output (dispatch control signals).

**Estimated effort:** 300 lines new, requires streaming support in dispatch layer.

---

## 4. Relationship to Existing Machinery

The `DynamicManager` already has most of the decision logic:

- **Role assignment:** determines who leads (`player_manager`) and who follows (`participant`). Currently unused in dispatch ordering.
- **Capability fingerprints:** `D_decay`, `v_bar`, `A`, `C` per model. Can drive dispatch ordering (highest `A` first for analytical tasks, highest `C` first for creative tasks).
- **`pre_decompose_models`:** immune-driven prompt sizing. Extends naturally to immune-driven pacing signals.
- **`dispatch_check` / `feasibility_probability`:** pre-dispatch gate. Extends to multi-step dispatch planning (can this model handle the full sequence, or does it need `STEP_BY_STEP`?).
- **Remediation chains:** escalating fixes for pathologies. Currently parameter adjustment only. Extends to dispatch strategy adjustment (parallel to sequential to multi-step).
- **Event stream:** `ManagerEvent` with typed events. Add `DISPATCH_SEQUENCED`, `PACING_SIGNAL`, `ATTRIBUTION_CONFLICT` event types.
- **`ConvergenceDetector`:** measures finding similarity. With attribution, can distinguish independent convergence from echo convergence.

The runner (`run_exp17_immune.py`) is the integration gap. It calls `DynamicManager` for stop conditions and telemetry but bypasses it for dispatch decisions. The whole body architecture closes this gap: the runner becomes a thin execution layer, and `DynamicManager` controls what gets dispatched, in what order, with what pacing, and with what context.

---

## 5. What This Is Not

This is not a chatbot or a multi-agent debate system. The models are not having a conversation. They are participating in a structured falsification process where:
- The immune layer controls information flow.
- The load balancer controls resource allocation.
- The convergence detector determines when to stop.
- The human (founder) retains override authority at every level.

The "conversation" is between the system and each model, not between models. Models never dispatch to each other. The `DynamicManager` mediates all communication. This is deliberate: it prevents models from forming consensus without independent verification, which is the central failure mode that CDSFL is designed to prevent.

The biological metaphor: organs do not talk to each other directly. The nervous system and circulatory system carry signals between them. The brain (human oversight) can override any signal. The immune system detects when something goes wrong and initiates corrective action. The whole body works because every component has a defined role and a controlled communication channel.

---

## 6. Success Criteria

**Phase 1 succeeds when:** findings carry attribution, and `format_findings_for_context` shows source model per finding.

**Phase 2 succeeds when:** within a single round, later models produce findings that explicitly reference earlier models' findings (by ID and source), and the convergence detector can distinguish independent convergence from echo.

**Phase 3 succeeds when:** a model receiving `STEP_BY_STEP` pacing produces findings of equal or higher quality (measured by severity, abstraction index, and human assessment) compared to single-shot dispatch, while consuming fewer prompt tokens per finding.

**Phase 4 succeeds when:** the immune layer terminates a dispatch mid-stream based on output quality monitoring, and the replacement dispatch produces better findings.

**Overall success:** the distributed compute pipeline produces findings faster, with higher quality, and with lower token cost per finding than the current parallel broadcast architecture. Measured against Experiment 17 as baseline.

---

## 7. Trigger

This work begins after Experiment 17 completes and findings are collated. Phase 1 can be implemented immediately. Phases 2–4 are the architectural evolution of the runner toward the system described in the CDSFL paper's distributed compute section.

The stopping criterion remains the founder's: "Everything wired and fully operational to an extent that we can turn it against the bench without wasted effort." The whole body architecture serves this criterion by making each dispatch more efficient and each finding more trustworthy.
