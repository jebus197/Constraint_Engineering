# CDSFL Architecture

How the system works. Read this after the GLOSSARY if you are new to the project.

For a visual overview of the complete system, see the **[Whole-Body Topology Map](CDSFL_Topology.svg)** — a single diagram showing every component and how they connect, using the biological paradigm that informed the design.

---

## Overview

CDSFL operates a panel of frontier language models under structured Popperian falsification. The system produces findings (first-order cognition), monitors its own analytical performance (second-order cognition), and adjusts based on that monitoring (metacognitive feedback). The architecture is substrate-agnostic: the same mechanisms apply whether agents are human, single-model, multi-model, hybrid human-machine, or — in principle — non-human biological intelligences. Evaluation does not privilege substrate at the level of its definitions.

Two orthogonal Popperian arms sit at the centre of the design. The **severe-tests arm** (§17 Feedback Channel, the FFAFP admissibility constraint set, cross-model corroboration, and tool-deterministic verification) filters claims. The **bold-conjectures arm** (§18 Divergence Directive, five dimensions of allowable variation, isomorphism suppression) forces generation. Neither arm is sufficient alone. The critic without the generator has nothing to filter; the generator without the critic hallucinates without correction.

## Components

### Runner (`bench/reference_runner_v2.py`, launched by `bench/launch_exp42.py`)

The runner orchestrates a multi-round analysis session: it composes prompts, dispatches them to models, parses responses, feeds findings through the immune pipeline, updates the registry, evaluates convergence, and manages checkpoints. Common infrastructure lives in `runner_core.py` and `experiment_11_orchestrator.py`.

`reference_runner_v2.py` (9,097 lines) has been the active runner for the Experiment 40–54 arc since 17 April 2026 and has driven every result from Experiment 40 onward. `reference_runner.py` (4,344 lines) is the frozen Experiment 38/39 baseline and is retained unchanged as a reference. Runs are launched through `bench/launch_exp42.py --config <config>` — a shared launcher for the whole arc whose name is historical, not Experiment-42-specific — which resolves the config, loads `.env`, and dispatches through `bench/launcher_core.py`. `bench/detached_launch.sh` wraps that in `nohup … & disown` for runs that must survive the terminal.

Experiments 29–37 have their own standalone `bench/run_exp*.py` scripts. Those are the pre-April-2026 harnesses, retained as records; they hand-parse `sys.argv`, silently ignore unrecognised flags, and dispatch live on launch.

### Model Dispatch (`bench/experiment_11_orchestrator.py`)

Central dispatch layer. Defines `ModelConfig` for each model (API endpoint, model ID, timeouts, retries) and routes calls to the correct API function. Five dispatch paths:

- **CC2**: Claude CLI (`claude -p`), system prompt via `--system-prompt` flag. Max subscription; never OpenRouter.
- **Codex / CX**: OpenRouter API, CDSFL as system role message
- **ChatGPT**: OpenRouter API, CDSFL as system role message
- **Gemini**: OpenRouter API (`google/gemini-3.1-pro-preview`), CDSFL as system role message; the direct Google GenAI SDK is retained as the secondary route only, since 2026-05-10 (`bench/experiment_11_orchestrator.py:166-177`)
- **DeepSeek**: DeepSeek API, CDSFL as system role message

Those are five dispatch paths over **four** distinct model identifiers. The Codex and ChatGPT seats both carry `model_id="openai/gpt-5.5"` on OpenRouter, with the same system prompt, the same role, and the same secondary route (`bench/experiment_11_orchestrator.py:139-164`). They differ by label and by the conversation history each accumulates, not by weights — so the panel is five seats over four models from four independent vendors.

OpenRouter function-calling tool-use is wired for cx, ge, cgpt, and ds (Experiment 40 Phase B, 1E.11). DeepSeek R1 also runs as a formal-verification specialist with confidence capped at 0.5 (1E.12).

### Directive Composition (`bench/cdsfl_registry/composer.py`)

Transforms the universal CDSFL directives into per-model phenotypes. Each model receives the same constraints but formatted for its characteristics: length caps, format density, example/rationale stripping. The three-layer composition: universal methodology (`cdsfl_core_formal.md`, `cdsfl_operational.md`, `cdsfl_topology_formal.md`), domain-specific directives, situation-specific context. The operational directive is loaded separately and appended post-composer so that recent additions (§15 FFAFP, §16 Stage 6, §17 Feedback, §18 Divergence) bypass phenotype caps and reach all five models.

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

Findings carry structured metadata: severity, description, evidence, proposed fix, model of origin, round of origin, verification status, admissibility block, novelty block (ν_k, c_ext, H/H_max, citations).

### Immune Pipeline (`bench/immune_agents.py`)

Cell-type verification system processing raw findings into classified outcomes. Modelled on biological immune response:

```
Raw Finding
    |
    v
[DC] Dendritic Cell -- intake, classification, AND-gate join
    |
    v
[CT] Cytotoxic T Cell -- code trace verification (300s timeout)
    |
    v
[B-Cell Complex] -- formal verification, manifest-driven specialist dispatch
    |       (first-definitive-verdict wins; see B-Cell section below)
    v
[NK Cell] -- deduplication (tau_sim 0.50, bug-closed gate)
    |
    v
[HT Cell] -- duplicate flagging across rounds
    |
    v
[RT Cell] -- reconciliation gate (three-path: LOCKED / UNSCORED / standard)
    |
    v
[Macrophage] -- monitoring (provenance, gate statistics, Ouroboros metrics)
    |
    v
[Ouroboros / O1] -- literature-novelty cell; live arXiv verification
    |
    v
Classified Finding -> Registry
```

Shadow (v1) and active (v2) pipelines run in parallel. v2 activation includes the LLM classifier (CLI Haiku via Max subscription, not OpenRouter), skin barrier, and enhanced cells.

### B-Cell Complex — Specialist Dispatch

The B-Cell is a composition of tool-specific verifiers, each a thin subprocess wrapper around an open-source tool. Dispatch is manifest-driven (`bench/cdsfl_registry/tool_manifest.toml` — 21 entries, of which 19 are direct and 2 are delegated; recounted with `tomllib` on 2026-08-07). Semantics: first-definitive-verdict wins; `[specialist:<tool>]` evidence suffix is preserved; `finding_id` is stamped on every verdict. Adding a new specialist is a TOML-only edit.

Active specialists (live domains):

- **Mathematics**: SymPy (symbolic), z3 (SMT / constraint), mpmath (arbitrary precision)
- **Statistics**: statsmodels, SciPy.stats
- **Biology**: Biopython (sequence validation)
- **Information science / ML**: scikit-learn, NetworkX (graph properties)
- **Uncertainty**: uncertainties, pint (dimensional analysis)
- **Code correctness**: mypy (types), ruff (lint), bandit (security), `dis` (bytecode), AST, CrossHair (symbolic execution / behavioural contracts)

Functional shadow specialists (promotion gated on empirical data from Experiment 41 onwards):

- **Physics**: astropy (constants, astronomical)
- **Chemistry**: RDKit (SMILES, molecule validation), stoichiometric balance
- **Engineering**: PuLP (linear programming), uncertainty propagation

Composition law (see `MATHEMATICAL_APPENDIX.md` and `FOUNDERS_NOTES.md` entry "Cell Type Architecture"): per-claim score S_k = A · E, where A is the product of all cell gates g_j (any cell voting zero rejects the claim) and E is the weighted aggregate of evidence e_m under confidence w_m. Specialist disagreement resolves by all parties needing to agree admissibility before confidence can grow, not by majority vote.

### Convergence System

Two independent mechanisms run every round:

**Primary gate**: Five boolean conditions tracked in `gate_history`. Fires when all five are simultaneously true for a sustained window. Conditions include γ threshold (scale-dependent: telemetry early, soft mid, hard late), open findings stability, inter-rater agreement, and others.

**Stall detector**: Secondary signal. Checks static open / contested counts plus γ threshold. Two tiers: advisory (γ ≥ 0.30, log only) and terminate (γ ≥ 0.45, fires STALL_CONVERGED).

**Two-sided critical-quiescence gate (the current terminal condition).** Since the Experiment 40 arc, the runner also evaluates a conjunctive gate over CRITICAL findings only. It fires when BOTH sides of the same diminishing-returns measure agree: `gamma_critical >= gamma_alt_threshold` (default 0.30 — the decay curve has flattened) AND a run of `gamma_alt_consecutive_zero_crit` consecutive rounds (default 3) in which no new genuine CRITICAL finding appeared, with no unverified critical pending, nothing contested, no churn, and the irreducible queue within bound. Both conditions are required; either alone is insufficient. Implemented at `bench/reference_runner_v2.py:2833-3035`. The exact pass condition for any run is printed by `python3 bench/launch_exp42.py --config <config> --dry-run`.

One narrowing applies: where the cumulative critical count over the whole run is zero, the critical decay curve does not exist and `gamma_critical` returns 0.0 — numerically identical to the worst case, a constant arrival rate. That case converges on the count side alone, guarded by a requirement that the panel produced findings of *some* severity, and it is logged distinctly as `CRITICAL_QUIESCENCE_CONVERGED (two-sided gate, VACUOUS CURVE)`. This narrows the estimator's domain; it does not weaken the gate.

Termination states emitted by `reference_runner_v2.py`, verified 2026-08-07:

| State | When |
|---|---|
| `STATE_CONVERGED` | primary five-condition gate held for the sustained window |
| `CRITICAL_QUIESCENCE_CONVERGED` | two-sided gate above (incl. the vacuous-curve variant) |
| `HARDENED_CONVERGED` | hardened gate — **opt-in only**, `hardened_gate_enabled` |
| `STALL_CONVERGED` | stall detector terminate tier |
| `EXTENSION_STALLED` | extension budget consumed without progress |
| `BUDGET_EXHAUSTED` | round or wall-clock cap reached |

The label `GAMMA_ALT_CONVERGED` appears in run records from before the two-sided gate was named; it is emitted by neither runner today.

### CC2v Verification Agent

CC2 dispatched between rounds to P-pass OPEN findings that the immune pipeline cannot mechanically verify. Produces structured verdicts (CONFIRM, REJECT, DUPLICATE, ESCALATE) at confidence threshold 0.7. Activates from round 6, batch size 6. ESCALATE bypasses confidence gating.

### Feedback Channel (§17, `bench/dm/_feedback.py`)

Closes the measurement-to-correction loop. Prior to §17, per-finding schema judgement (B-Cell verdicts, admissibility pass / fail, near-duplicate scores, R_k discrepancy) was logged and discarded; models never saw it. §17 assembles this signal into per-model prompt sections for the next round. Action precedence: REFUTED by tool > ADMISSIBILITY FAIL > NEAR-DUPLICATE > R_k INCONSISTENT. Imperative wording — flagged findings must be addressed, not merely acknowledged. Counter-receipts from the model's own tool are the only admissible challenge to a schema tool verdict. Unchanged flagged findings resubmitted in a subsequent round are inadmissible. Per-model routing; top-K cap (default 10); max-chars-per-model cap (default 8000). Live by default; toggle retained for controlled ablation. 533 LOC + ~90 lines directive + 39 tests.

### Divergence Directive (§18, `bench/dm/_divergence.py`)

Enforces the bold-conjectures arm. Each primary finding must be accompanied by at least one alternative that differs on one of five dimensions: **mechanism**, **assumption**, **scope**, **timescale**, **tradeoff**. Alternatives that are cosmetic rewordings are rejected by an isomorphism check (Jaccard over normalised token sets, default threshold 0.85, double penalty for isomorphic-only submissions). Structure A: primary + alternative on named dimension. Structure B: primary + scoped null-justification (minimum 60 characters, citing the dimension on which no alternative was possible). Divergence operates only in SOFT-constraint space — HARD constraints (physics, mathematics, law, safety) remain inviolable for primary and every alternative.

Channel assignment was resolved by a five-panel mathematical-convergence confer (15-16 April 2026, unanimous): the §18 multiplier is not on R_k but on η_int (the internal-novelty term), with structural compliance gated at FFAFP admissibility and continuous isomorphism suppression handled by w(f) in κ_set. The function was renamed `divergence_penalty_multiplier` → `eta_int_modulator` to make the channel explicit in the code name. 443 LOC + ~90 lines directive + 75 tests.

### Ouroboros Cell (O1) — Literature Novelty

Checks whether a claimed novel finding has already been published, whether a claimed reproduction matches its source, whether the panel is asserting originality the archive would dispute. Live arXiv verification as of Experiment 40 Phase B (17 April 2026). Inputs to the Stage 6 two-dimensional novelty score: ν_k (unprecedented against external sources) and c_ext (thoroughness of external search). Combined novelty η_combined = η_int · (1 − c_ext · (1 − ν_k)). Strong external search of an already-published finding pulls η_combined toward zero regardless of internal novelty.

### Macrophage Cell

System monitoring. Three modes: provenance (signed fingerprints, cross-experiment continuity), gate statistics (per-round gate-history metrics for HIL tracing), and Ouroboros metrics (literature-search yield, query quality, citation diversity). Wired in Experiment 39-0 gate work (14 April 2026).

### ITC (Intelligent Task Controller)

Adaptive recovery for model failures and degradation. Classifies failure type and applies targeted strategy:

- **restart_fresh**: New context with fingerprint-informed scope. Produces rediscoveries, not new defects.
- **change_focus**: Registry-aware redirect. Tells model to issue verdicts / merges rather than re-describe known issues.
- **decompose**: Breaks prompt into smaller chunks for context-constrained models.

Never benches models. Models are always restarted, never removed from the panel.

**Adaptive parse-yield detection** (Exp 39): Each model builds its own parse-yield history (rolling window of 20 rounds). Once 4+ entries exist, baseline = mean of best 3 of last 5 yields. Adaptive threshold = max(0.5 hard floor, baseline − 0.25). Models are judged against their own performance, not a static constant.

Design trade-offs (verified numerically, Exp 39 Round 3 confer, 2026-04-11):

- **Outlier resistance vs trend detection**: The "best 3 of 5" filter discards the worst two recent values, making it robust against single bad rounds but blind to sustained gradual degradation. At degradation rates below ~9% per round, the adaptive threshold never fires before the 0.5 hard floor — the filter absorbs the decline. At 9%+ per round, the adaptive threshold catches 2-3 rounds earlier than the floor. The adaptive threshold detects sharp drops; the hard floor is the safety net for gradual decline. Context overload causes gradual decline, so the floor is load-bearing there.
- **Anti-gaming**: Front-loading high-quality rounds to establish a generous baseline backfires only when the gap between front-loaded and true performance exceeds the deviation margin (0.25). A model at true 70% must front-load above 95% to trigger detection.
- **Phase persistence**: `_itc_model_state` (including yield history) persists across burst-mode phase transitions. Parse yield is a model characteristic, not a phase characteristic. Only `restart_fresh` resets it.
- **Ordering invariant**: `_itc_detect` must run before `_update_observed_fingerprint` in the per-model loop.

### Endocrine Layer (`bench/endocrine.py`)

Health monitoring subsystem. Runs periodic health cycles computing diagnostics. Provides pacing signals (slow down / speed up based on system state) and a fix-evaluation sandbox (pyright, ruff, bandit, pytest in isolation).

### Verification Chain (`bench/verification_chain.py`)

Cryptographic audit trail implementing RFC 9162. Hash chains with Ed25519 signing, epoch sealing, and inclusion proofs. Every finding is hashed into the chain. Provides tamper-evident records.

### PolicyEngine (`bench/cdsfl_registry/`)

Hierarchical constraint enforcement. Five-layer cascade: foundation, domain, task, session, model-specific. Monotonicity invariant: lower layers cannot weaken higher-layer HARD constraints. Manages the TOML-based policy schema (`schema.toml`). The PolicyEngine is not the registry — it enforces the rules; the registry stores the findings.

### Insect Brain (`bench/insect_brain.py`)

Central coordination hub. Manages checkpoint persistence (save / restore experiment state), round coordination, relay-mode message routing, and convergence signalling. Named for its role as a minimal but essential coordination point.

### Component Maturity (Closure-State Lexicon)

Every code component in the pipeline carries one of four maturity labels (the F4 lexicon, locked 21 April 2026 with `tripwire` added 13 May 2026):

| Label | Definition | Drives outcomes? |
|---|---|---|
| `library_complete` | Code present and tested, not hooked into any live or shadow pipeline path. | No |
| `tripwire` | Hooked into the pipeline; observation-only by default, assertive when an explicit flag is set. | Only when flag is set |
| `shadow_integrated` | Hooked into the live pipeline in observation-only capacity; emits logs and metrics but does not drive verdicts, promotions, or gate decisions. | No |
| `live_operational` | Drives live decisions; reversion requires explicit policy change. | Yes |

Promotion order: `library_complete` → `tripwire` (if applicable) → `shadow_integrated` → `live_operational`. The `tripwire` tier is optional; most components flow directly through shadow to live. The Component Closure-State Index at the F4 lexicon section in `resources/ONBOARDING.md` is the canonical source for each component's current label.

## Target Kind: the prose path

The harness was built to review Python modules and now also reviews technical
PROSE documents — exam modules and design references whose claims are argued in
text, tables and equations. The target kind (`python` or `prose`) is resolved by
the harness from the target itself; a configuration may declare it, and a
disagreement vetoes the run, but a declaration can never redirect the
classification.

**Prose is fully reviewable. What changes is which mechanisms apply, not whether
the target is computable.** Specialist routing keys on CLAIM TYPE — mathematical,
logical, statistical, code-structural, code-behavioural — not on document type,
and 14 of the 21 tools in `tool_manifest.toml` are claim tools indifferent to
whether a claim arrived in prose or in a comment. Only file-based Python-source
tools are affected, because ruff, mypy and bandit cannot read a markdown file;
they are bypassed and reported NOT_APPLICABLE rather than run and believed.

Four mechanisms differ on a prose target:

| mechanism | on a Python target | on a prose target |
|---|---|---|
| Fix admission (S_k) | scored | **NO_SCORE** — undefined over this substrate; on prose it inverts |
| Fix verification | ruff/mypy/bandit/tests → PASS closes | **NO_APPLICABLE_CHECKS** — a syntax veto may reject, never close |
| Routing-ladder prompt | "import the real module" | the document's **path and text**, "open it by path" |
| Panel round briefing | fixes are linted, tested and CLOSED | a fix cannot close; a **runnable falsifier** settles it |

The settlement route on a prose target is therefore the falsifier gate alone: a
test that opens the document by path and asserts on its text, or on a value
recomputed from it, or on a listing extracted from it — re-executed by the runner,
never taken on the model's word.

**The routing ladder is the only absorber between the falsifier gate and the human
queue**, which is why the launch preflight refuses to start a prose run with it
disabled. Its prompt was code-only until 2026-08-01: it received neither the
target's path nor its text, so on a document containing fenced code listings no
rung could resolve anything and the recorded reason — "no model produced a
runnable test" — was false, because no model was ever given the target. Measured
after the repair on the same findings: 6 of 8 resolved against a prior null of 0
of 25 (Fisher exact p = 2.5×10⁻⁵).

## Data Flow (One Round)

```
1. Runner reads registry state and composes per-model prompts
   (composer transforms CDSFL directives + registry summary + round
    context + §17 feedback sections if available)

2. Runner dispatches prompts to all 5 models in parallel
   (each model receives CDSFL as system prompt, task as user prompt;
    §18 requires alternatives or scoped null-justification per finding)

3. Models return findings in structured format
   (parser extracts finding ID, severity, description, evidence, fix,
    ADMISSIBILITY block, NOVELTY block)

4. Findings enter immune pipeline
   (DC -> CT -> B-Cell Complex -> NK -> HT -> RT -> Macrophage -> Ouroboros)

5. Classified findings update the registry
   (status transitions: OPEN, CONFIRMED, CONTESTED, MERGED, etc.)

6. CC2v verification runs on batch of OPEN findings (from round 6+)
   (CONFIRM/REJECT/DUPLICATE/ESCALATE verdicts feed back to registry)

7. §18 divergence audit runs per finding
   (eta_int_modulator applied to internal novelty; isomorphic
    alternatives rejected)

8. Convergence gate evaluates all 5 conditions
   (gate_history updated, primary + stall detector both run)

9. ITC evaluates per-model performance
   (fingerprint update, degradation detection, strategy selection)

10. §17 feedback assembled for next round
    (per-finding schema judgment rendered as per-model prompt sections)

11. Runner checkpoints state (registry, gate history, stall history,
    feedback sections)

12. Next round begins or experiment terminates
```

## Communication Topologies

**Star / Blackboard**: Models interact only with the central registry. No model-to-model messaging. Runner owns all state. Used from Experiment 33 onwards as the default.

**Relay**: Models exchange messages through the insect brain. Three sub-modes: findings only, conversational (models see reasoning), directed (explicit model-to-model addressing). Runtime switch (`--topology relay|star`) since Experiment 35.

The shared verification infrastructure (finding registry, convergence gate, immune pipeline, endocrine monitor, verification chain) is indifferent to topology. Topology is a parameter, not an architectural commitment.

## Mathematical Framework

The full mathematical framework is in [`docs/MATHEMATICAL_APPENDIX.md`](MATHEMATICAL_APPENDIX.md). Three canonical stages:

**Stage 1 — Reference (C(n)):** Simple corroboration as the baseline mathematical object. Geometric form. Referenced but not used operationally.

**Stages 5-6 — Operational (R_k(i)):** Unified recursive self-assessment equation. Each model computes q = d_ik · p_ik per round, then R_det = R_k(i-1) · (1 − q) / (1 − q · R_k(i-1)), then R_k(i) = R_det · (1 − ν_k) + ν_k. Log-odds form: logit(R_det) = logit(R_k(i-1)) + log(1 − q). Critical re-injection rate ν* = q · R. R_k(i) replaces C(n) in all operational directives. The Popperian propensity parameter π vanishes from the recursion (8 April 2026 derivation).

**Stage 6 extension — Literature-calibrated novelty:** Two-dimensional (ν_k, c_ext). η_combined = η_int · (1 − c_ext · (1 − ν_k)). The §18 divergence multiplier attaches to η_int, not R_k (unanimous five-panel resolution, 15-16 April 2026).

Other quantities:

- **F_n**: Structured falsification coverage
- **D(n)**: Distributed compute coverage
- **G_n**: Detection coverage of the composite system (Stage 1 reference)
- **γ**: Duane NHPP convergence parameter
- **ρ**: Discovery efficiency (novel / raw)
- **H(x)**: Abstraction index (finding depth)
- **κ_set**: Set-level convergence with continuous weight w(f)
- **S_k**: Per-claim composite score (A · E; see B-Cell Complex)
- **FFAFP admissibility set**: S_min, G-completeness, d_tool, σ_measured, q_retest (§15 of operational directive)

See [`docs/MATHEMATICAL_APPENDIX.md`](MATHEMATICAL_APPENDIX.md) §1.1, §1.6, §1.7, §1.8 for the Stage 6 extension and §3, §16 of `bench/directives/universal/cdsfl_operational.md` for the operative directives.
