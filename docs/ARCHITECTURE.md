# CDSFL Architecture

How the system works. Read this after the GLOSSARY if you are new to the project.

For a visual overview of the complete system, see the **[Whole-Body Topology Map](CDSFL_Topology.svg)** — a single diagram showing every component and how they connect, using the biological paradigm that informed the design.

---

## Overview

CDSFL operates a panel of frontier language models under structured Popperian falsification. The system produces findings (first-order cognition), monitors its own analytical performance (second-order cognition), and adjusts based on that monitoring (metacognitive feedback). The architecture is substrate-agnostic — the same mechanisms work regardless of whether agents are human or machine.

## Components

### Runner (`bench/run_exp*.py`)

Each experiment has its own runner script. The runner orchestrates a multi-round analysis session: it composes prompts, dispatches them to models, parses responses, feeds findings through the immune pipeline, updates the registry, evaluates convergence, and manages checkpoints. All runners share common infrastructure from `runner_core.py` and `experiment_11_orchestrator.py`.

### Model Dispatch (`bench/experiment_11_orchestrator.py`)

Central dispatch layer. Defines `ModelConfig` for each model (API endpoint, model ID, timeouts, retries) and routes calls to the correct API function. Five dispatch paths:

- **CC2**: Claude CLI (`claude -p`), system prompt via `--system-prompt` flag
- **Codex/CX**: OpenRouter API, CDSFL as system role message
- **ChatGPT**: OpenRouter API, CDSFL as system role message
- **Gemini**: Google GenAI SDK, CDSFL as `system_instruction`
- **DeepSeek**: DeepSeek API, CDSFL as system role message

### Directive Composition (`bench/cdsfl_registry/composer.py`)

Transforms the universal CDSFL directives into per-model phenotypes. Each model receives the same constraints but formatted for its characteristics: length caps, format density, example/rationale stripping. The three-layer composition is: universal methodology, domain-specific directives, situation-specific context.

### Finding Registry (`bench/runner_core.py`)

Central blackboard in star topology. Maintains canonical finding entries with a defined status FSM:

```
OPEN -> CONFIRMED (2+ independent models agree)
OPEN -> CONTESTED (late challenge after confirmation)
OPEN -> MERGED (merge verdict from a model)
CONFIRMED -> CLOSED (verified fix applied and passing)
CLOSED -> REOPEN (new evidence, auto-escalates to HIL)
Any non-MERGED -> UNCONFIRMED (end of experiment, not resolved)
```

Findings carry structured metadata: severity, description, evidence, proposed fix, model of origin, round of origin, verification status.

### Immune Pipeline (`bench/immune_agents.py`)

Six-cell-type verification system processing raw findings into classified outcomes. Inspired by biological immune response:

```
Raw Finding
    |
    v
[DC] Dendritic Cell -- intake and classification
    |
    v
[CT] Cytotoxic T Cell -- code trace verification (300s timeout)
    |
    v
[B Cell] -- formal verification (SymPy, Z3 SMT, AST)
    |
    v
[NK Cell] -- deduplication (tau_sim 0.50, bug-closed gate)
    |
    v
[HT Cell] -- duplicate flagging across rounds
    |
    v
[RT Cell] -- reconciliation gate (three-path: LOCKED/UNSCORED/standard)
    |
    v
Classified Finding -> Registry
```

Shadow (v1) and active (v2) pipelines can run in parallel. v2 activation includes the LLM classifier, skin barrier, and enhanced cells.

### Convergence System

Two independent mechanisms run every round:

**Primary gate**: Five boolean conditions tracked in `gate_history`. Fires when all five are simultaneously true for a sustained window. Conditions include gamma threshold (scale-dependent: telemetry early, soft mid, hard late), open findings stability, inter-rater agreement, and others.

**Stall detector**: Secondary signal. Checks static open/contested counts plus gamma threshold. Two tiers: advisory (gamma >= 0.30, log only) and terminate (gamma >= 0.45, fires STALL_CONVERGED).

Four possible termination states: STATE_CONVERGED, STALL_CONVERGED, EXTENSION_STALLED, BUDGET_EXHAUSTED.

### CC2v Verification Agent

CC2 dispatched between rounds to P-pass OPEN findings that the immune pipeline cannot mechanically verify. Produces structured verdicts (CONFIRM, REJECT, DUPLICATE, ESCALATE) at confidence threshold 0.7. Activates from round 6, batch size 6. ESCALATE bypasses confidence gating.

### ITC (Intelligent Task Controller)

Adaptive recovery for model failures and degradation. Classifies failure type and applies targeted strategy:

- **restart_fresh**: New context with fingerprint-informed scope. Produces rediscoveries, not new defects.
- **change_focus**: Registry-aware redirect. Tells model to issue verdicts/merges rather than re-describe known issues.
- **decompose**: Breaks prompt into smaller chunks for context-constrained models.

Never benches models. Models are always restarted, never removed from the panel.

### Endocrine Layer (`bench/endocrine.py`)

Health monitoring subsystem. Runs periodic health cycles computing diagnostics. Provides pacing signals (slow down / speed up based on system state) and a fix evaluation sandbox (pyright, ruff, bandit, pytest in isolation).

### Verification Chain (`bench/verification_chain.py`)

Cryptographic audit trail implementing RFC 9162. Hash chains with Ed25519 signing, epoch sealing, and inclusion proofs. Every finding is hashed into the chain. Provides tamper-evident records.

### PolicyEngine (`bench/cdsfl_registry/`)

Hierarchical constraint enforcement. Five-layer cascade: foundation, domain, task, session, model-specific. Monotonicity invariant: lower layers cannot weaken higher-layer HARD constraints. Manages the TOML-based policy schema.

### Insect Brain (`bench/insect_brain.py`)

Central coordination hub. Manages checkpoint persistence (save/restore experiment state), round coordination, relay-mode message routing, and convergence signalling. Named for its role as a minimal but essential coordination point.

## Data Flow (One Round)

```
1. Runner reads registry state and composes per-model prompts
   (composer transforms CDSFL directives + registry summary + round context)

2. Runner dispatches prompts to all 5 models in parallel
   (each model receives CDSFL as system prompt, task as user prompt)

3. Models return findings in structured format
   (parser extracts finding ID, severity, description, evidence, fix)

4. Findings enter immune pipeline
   (DC -> CT -> B Cell -> NK -> HT -> RT)

5. Classified findings update the registry
   (status transitions: OPEN, CONFIRMED, CONTESTED, MERGED, etc.)

6. CC2v verification runs on batch of OPEN findings (from round 6+)
   (CONFIRM/REJECT/DUPLICATE/ESCALATE verdicts feed back to registry)

7. Convergence gate evaluates all 5 conditions
   (gate_history updated, primary + stall detector both run)

8. ITC evaluates per-model performance
   (fingerprint update, degradation detection, strategy selection)

9. Runner checkpoints state (registry, gate history, stall history)

10. Next round begins or experiment terminates
```

## Communication Topologies

**Star / Blackboard**: Models interact only with the central registry. No model-to-model messaging. Runner owns all state. Used in Experiments 33-36.

**Relay**: Models exchange messages through the insect brain. Three sub-modes: findings only, conversational (models see reasoning), directed (explicit model-to-model addressing). Used in Experiments 29-31.

## Mathematical Framework

The full mathematical framework is in `docs/MATHEMATICAL_APPENDIX.md` (1081 lines). Key quantities:

- **C(n)**: Simple corroboration (baseline model)
- **F_n**: Structured falsification coverage
- **D(n)**: Distributed compute coverage
- **R_n**: Residual risk after clean run
- **G_n**: Detection coverage of the composite system
- **gamma**: Duane NHPP convergence parameter
- **rho**: Discovery efficiency (novel/raw)
- **H(x)**: Abstraction index (finding depth)
- **Y(t)**: Cognitive yield (count times mean depth)
- **Y_composite**: Composite system yield (emergence metric)

Five structural gaps between the appendix and experimental evidence have been identified (see `experimental_notes/Exp36_Mathematical_Model_Audit_2026-04-07.md`). Audit execution pending.
