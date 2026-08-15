# CDSFL Glossary

Every term, acronym, Greek letter, and component name used in the project.
Alphabetical. If a term is not here, it should be added.

---

### Abstraction Index (H(x))

Measures finding depth: formality times information density times generalisation scope. Captures the difference between spotting a typo and identifying a paradigm-level architectural flaw. Defined in Mathematical Appendix Section 7.2.

### B Cell

Immune pipeline cell type. Stage 3 verification agent. B Cell v1 uses SymPy for mathematical claim verification. B Cell v2 adds AST (Abstract Syntax Tree) analysis and Z3 SMT (Satisfiability Modulo Theories) solver for formal verification. Produces structured verdicts.

### Blackboard

Communication topology where models share state through a central FindingRegistry rather than direct messaging. Models see only the registry summary, not each other's raw output. See also Star topology.

### CC1

Claude Code running in UX (interactive) mode, currently Opus 4.7. The operator instance — runs the conversation, coordinates work. Not a panel participant. Uses the Max subscription. The model version is rotated; the roster of record is `docs/REPRODUCING.md` § Model Confer Dispatch.

### CC2

Claude Code running in piped mode (`claude -p`), currently Opus 4.7. Headless CLI instance dispatched via the Claude binary. Used as verification agent (CC2v) in runners and available for confer. Same Max subscription as CC1. Version rotates with CC1; same roster of record.

### CC2v

CC2 verification agent. Runs between rounds in the experiment runners. P-passes OPEN findings that the immune pipeline cannot mechanically verify. Produces structured verdicts: CONFIRM, REJECT, DUPLICATE, ESCALATE. Confidence-gated at 0.7. Activates from round 6.

### CDSFL

Constraint-Driven Synthesis and Falsification. The protocol-level architecture for scientific cognition that this project implements. Formalises Popperian falsification as a structured protocol for multi-model analytical collaboration.

### C(H,E)

Popper's degree of corroboration. Measures how well evidence E supports hypothesis H given background knowledge. Used in the runner to track overall corroboration of findings. Defined in the white paper Section 2.1.

### Closure-State Labels (F4 lexicon)

Four-label vocabulary describing a code component's maturity within the runtime pipeline. Locked 21 April 2026 (three labels); extended 13 May 2026 (added `tripwire`). Full definitions in `resources/ONBOARDING.md` under "Closure-State Lexicon". Promotion order: `library_complete` → `tripwire` (if applicable) → `shadow_integrated` → `live_operational`. The `tripwire` tier is optional and applies specifically to flag-gated runtime guards.

- **`library_complete`** — code present and tested, not hooked into any live or shadow pipeline path.
- **`tripwire`** — code hooked into the pipeline, observation-only by default (off, or on-emit-only), but becomes assertive (halts the run, blocks the gate, drives an outcome) when an explicit flag is set. Example: `DEBUG_CHANNEL_CHECK` assertion at `bench/reference_runner_v2.py:3510`.
- **`shadow_integrated`** — code hooked into the live pipeline in observation-only capacity. Runs on every relevant input, emits logs and metrics, but does not drive verdicts, promotions, or gate decisions. Example: K/L/M shadow-audit logging.
- **`live_operational`** — code drives live decisions; outputs affect verdicts, gates, or downstream state. Reversion requires explicit policy change. Examples: §17 feedback directive, §18 divergence directive.

### Composer

The directive composition system (`bench/cdsfl_registry/composer.py`). Produces per-model phenotype-transformed versions of CDSFL directives. Each model receives the same underlying constraints but formatted for its processing characteristics (length caps, format density, stripping levels).

### Confer/Defer

Multi-model protocol. Confer: models review each other's findings iteratively, seeking convergence. Defer: escalation to HIL when models cannot resolve a disagreement. The confer protocol forces agents into analytical territory none explored alone.

### Convergence Gate

Primary termination mechanism. Five boolean conditions evaluated per round, tracked in gate_history. Fires when all five conditions are simultaneously true for a sustained window. Conditions include gamma threshold, open findings stability, inter-rater agreement, and others. Defined in topology spec T4.

### Computed Evidence

A record attached to a CRITICAL finding that the machinery may not clear
automatically, carrying the answer it nevertheless worked out: the verdict, the
model that produced it, the falsifier that ran, and the panel's proposed fix. A
critical is never retired by a refutation — CONFIRM-only stands, because on
Exp 42 two of three REFUTED verdicts on criticals were themselves wrong — but the
computation is no longer discarded. The finding and the evidence reach the human
together. Founder ruling, 2026-08-03. See `_record_computed_evidence`.

### CT Cell (Cytotoxic T Cell)

Immune pipeline cell type. Stage 2 code trace verification. Executes concrete code traces to verify or refute finding claims. CT v2 adds falsification — actively tries to construct counterexamples. Timeout: 300 seconds.

### CX

Codex, GPT-5.4 dispatched via OpenRouter API. Originally ran via `codex exec` CLI with OpenAI's agent system prompt; moved to OpenRouter at Run 6 for reliability. See Model Panel Config memory file for full detail.

### DC Cell (Dendritic Cell)

Immune pipeline cell type. Stage 1 intake. Receives raw findings, performs initial classification, routes to appropriate verification cells.

### Decay Curve (D)

Plot of finding rate over rounds. Genuine analysis produces diminishing rates (Duane NHPP model, gamma greater than 0). Chatbot churn produces flat curves (gamma approximately 0). The shape distinguishes analysis from noise.

### Decomposition

Strategy for context-constrained models. When a prompt exceeds a model's context budget, it is decomposed into smaller chunks dispatched sequentially. DeepSeek always runs decomposed (threshold 0). See `bench/decomposed_dispatch.py`.

### Discovery Efficiency (rho)

Ratio of novel findings to raw findings per round. Captures information that gamma misses: raw output can be high while novelty is low. Not yet formalised in the Mathematical Appendix (Gap 2 in the model audit). Invented during Experiment 36.

### Duane NHPP

Non-Homogeneous Poisson Process model used to estimate gamma (convergence parameter). Applied to cumulative novel finding counts across rounds. Log-log regression over canonical novelty counts. Named after J.T. Duane (1964).

### Emergence

When multiple agents work under structured falsification, the composite system's cognitive yield Y exceeds any individual's. Formalised in Mathematical Appendix Section 8.2. Strong emergence condition: Y_composite exceeds Y_union plus z times sigma-hat.

### Endocrine Layer

Health monitoring subsystem (`bench/endocrine.py`). Runs periodic health cycles computing diagnostics across security, dead code, type safety, null deref, and style categories. Provides pacing signals and fix evaluation sandbox.

### Falsifier, and the falsifier gate

A falsifier is a runnable program attached to a finding that imports the real target (or opens the real document) and demonstrates the defect. Under the falsifier gate (`falsifier_gate_enabled`) the runner independently re-executes it, and **that** verdict — never the model's prose — decides the finding. Four outcomes, defined at `bench/falsifier_verify.py:120-150`:

- **CONFIRMED** — the re-run actively demonstrated the defect: it raised an `AssertionError` or printed the literal token `FALSIFIED`.
- **REFUTED** — the falsifier ran to a clean exit and demonstrated nothing.
- **UNTOOLABLE** — no falsifier code was supplied.
- **ERROR** — timeout, harness failure, or a non-zero exit that is not a genuine demonstration (a broken falsifier: bad import, typo, raw exception).

The asymmetry is deliberate. A CONFIRMED requires an active demonstration, which is hard to fake; a clean exit is never promoted to a confirmation. On a CRITICAL finding the gate is CONFIRM-only: REFUTED, ERROR, UNTOOLABLE, or a critical with no falsifier all escalate to the human rather than being auto-resolved, because a logically broken falsifier exits cleanly and would otherwise mask a real defect.

The falsifier source and its verdict are both preserved in a run's report, under `registry.entries[<id>].falsifier_code` and `.falsifier_verdict`.

### f_del (Delivery Feasibility)

Parameter modelling the probability that a model can successfully deliver findings given its current context state. Degrades with context size but currently modelled as a constant (Gap 4 in the model audit).

### FFAFP (Find-Follow-Analyse-Fix-P-pass)

Five-step intra-model reasoning cycle. (1) Find the issue, its location, and the evidence. (2) Follow consequences through the entire system before touching anything — trace dependencies, interfaces, downstream effects. (3) Analyse dispassionately with available tools (CONFIRMED, UNCERTAIN, or REJECTED). (4) Fix with the simplest sufficient correction addressing root cause and downstream consequences. (5) P-pass: actively try to disprove the fix. Triggered by the `f` metacognitive command. Supersedes the original 3-step FFF (Find-Follow-Fix) and the 4-step FFAF (Find-Follow-Analyse-Fix).

### FFF (Find-Follow-Fix) [DEPRECATED]

Original 3-step intra-model reasoning cycle. Superseded by FFAFP. Historical references in experiment logs reflect the protocol used at the time of those experiments.

### FindingRegistry

Central blackboard data structure in star topology. Maintains canonical finding entries with status (OPEN, CONFIRMED, CONTESTED, MERGED, UNCONFIRMED, CLOSED). Programmatic status transitions. Persists across rounds via checkpoints.

### Fingerprint

Four-dimensional capability profile per model: (D, v-bar, A, C). D equals decay rate, v-bar equals verification score (fraction confirmed by SymPy or similar), A equals total verified findings, C equals coverage of constraint space. Used by ITC for targeted interventions.

### Gamma (gamma)

Duane NHPP convergence parameter. Estimated from cumulative novel findings via log-log regression. Gamma greater than 0 indicates discovery rate depletion (convergence). Gamma approximately 0 indicates churn. Gamma less than 0 indicates divergence. Gap 1 in the model audit: gamma misclassifies system-level churn because it only sees novel rate, not raw-to-novel divergence.

### Gamma_critical (gamma_critical)

The Duane NHPP decay parameter computed over CRITICAL findings only, as distinct from `gamma`, which is computed over all findings. **`gamma_critical` is the input to the two-sided convergence gate; `gamma` is telemetry** — the runner's own terminal reason string labels it so. Both series are recorded per run as `gamma_critical_history` and `gamma_history` (a third, `gamma_all_history`, also appears in reports). Quoting one under a bare label "Gamma" is ambiguous; always name the series.

### HARD/SOFT Classification

Constraints classified as non-negotiable (HARD) or preference-based (SOFT). HARD constraints include physics, mathematics, law, safety, and explicit absolutes. SOFT constraints include economic, preference, and convenience. Ambiguous defaults to HARD.

### HIL (Human-in-the-Loop)

Founder review. Findings escalated to HIL when models cannot resolve disagreements, when CC2v assigns ESCALATE verdict, or when contested findings persist beyond threshold. HIL decisions are final within the experiment scope.

### HT Cell (Helper T Cell)

Immune pipeline cell type. Duplicate detection. HT v2 flags approximate duplicates per round using similarity matching. Helps reduce churn by identifying when models are re-describing known issues.

### Irreducible-Queue Alarm

Fires when the number of findings locked in an unresolvable state exceeds a bound
(default 2). Its premise is that a large pile of genuinely irreducible findings
almost always indicates broken machinery rather than an unusually hard document —
vindicated on 2026-08-01, when the pile was caused by a routing ladder that never
received the target and raising the bound twice was wrong both times. Since
2026-08-02 it HALTS the run rather than merely refusing to declare convergence.

### Immune Pipeline

Six-cell-type verification system inspired by biological immune response. Stages: DC (intake) then CT (code trace) then B Cell (formal verification) then NK (deduplication) then HT (duplicate flagging) then RT (reconciliation). Processes raw findings into verified, rejected, or escalated classifications.

### Insect Brain

Central relay module (`bench/insect_brain.py`). Manages checkpoint persistence, round coordination, model dispatch in relay mode, and convergence signalling. Named for its role as a minimal coordination hub.

### ITC (Intelligent Task Controller)

Adaptive recovery system. Classifies model failures and applies corrective strategies. Key strategies: restart_fresh (new context), change_focus (redirect attention via registry), decompose (break into chunks). Never benches models. Gap 3 in the model audit: ITC feedback loop (restart_fresh creating rediscoveries) is not modelled.

### Kappa (kappa)

Inter-rater agreement metric. Measures the degree of consensus among models on finding status. Used as one of the convergence gate conditions. Computed from status agreement across the finding registry.

### Merkle Tree

RFC 9162 (CDSFL) and RFC 6962 (OpenBrain, Genesis) hash tree structure providing cryptographic verification. Each finding is hashed and incorporated into a tree. Inclusion proofs demonstrate that a specific finding was part of a sealed epoch. Implemented in `bench/verification_chain.py`.

### Launch Preflight (A9)

Three checks that REFUSE to start a run whose machinery contradicts its target:
the target exists and is non-empty; routing is enabled on a prose target (it is
the only absorber between the falsifier gate and the human queue); and the
falsifier gate is enabled on a prose target (with S_k off and fix-verification
unable to close, it is the only route to a terminal state). Deliberately short —
everything the harness can correct at runtime it corrects at runtime, and a
preflight that re-litigated those would be noise. It raises; it does not warn.

### NK Cell (Natural Killer Cell)

Immune pipeline cell type. Stage 4 deduplication. NK v1 uses Jaccard similarity for finding matching. NK v2 adds tau_sim threshold (0.50), intra-round deduplication, and the bug-closed gate (first verified fix wins, subsequent findings about the same bug rejected). Convergence tau_sim (0.33, for clustering) is decoupled from immune tau_sim.

### P-Pass

Popperian falsification pass. Generate a conclusion, actively try to disprove it, repair if falsified, repeat until diminishing returns. The core mechanism of CDSFL. Up to five passes for standard P-pass. Can be invoked with shorthand `p`.

### phi_fmt (Format Yield)

Parameter modelling a model's ability to produce correctly formatted output. Degrades with context size but currently modelled as a constant (Gap 4 in the model audit, coupled with f_del).

### PolicyEngine

Hierarchical constraint enforcement system (`bench/cdsfl_registry/`). Five-layer cascade with monotonicity: lower layers cannot weaken higher-layer HARD constraints. Layers: foundation, domain, task, session, model-specific. Not "the registry" (standing correction).

### Relay Mode

Communication topology where models exchange messages through the insect brain as central relay. Models see each other's reasoning. Three sub-modes: findings, conversational, directed. Contrast with star (blackboard) topology.

### Rho (rho)

Discovery efficiency: novel findings divided by raw findings per round. See Discovery Efficiency.

### RT Cell (Regulatory T Cell)

Immune pipeline cell type. Stage 6 reconciliation. Final gate that ensures consistency across all verification results. Three-path reconciliation: LOCKED (high confidence, tool-verified), UNSCORED (low confidence, absence of evidence), standard agreement.

### Runner

The Python program that orchestrates a multi-model analysis session. Since Experiment 40 there is one active runner, `bench/reference_runner_v2.py`, driven by the shared launcher `bench/launch_exp42.py` and selected per experiment by a committed config under `bench/expNN_configs/`; the launcher's name is historical, not Experiment-42-specific. `bench/reference_runner.py` is the frozen Experiment 38/39 baseline. Experiments 29–37 each have their own standalone script (e.g. `run_exp36_evidence.py`), retained as records. All share infrastructure from `runner_core.py` and `experiment_11_orchestrator.py`.

### S_k Tristate, and NO_SCORE

The fix-admission score reports ADMISSIBLE, REJECTED, ESCALATE or **NO_SCORE**.
NO_SCORE is not a third grade of admissibility: it is the statement that S_k has
no opinion, because the target is not the substrate S_k is defined over. On a
prose target S_k does not merely fail to help, it inverts — measured 2026-08-01,
a fix injecting a shell-injection call into a fenced listing scored 1.0000
ADMISSIBLE while a correct prose fix scored 0.6667. Fix efficacy then enters the
residual-risk term as zero rather than as a misleading number.

### Second-Order Cognition

System that analyses problems (first-order), monitors its own analytical performance (computes gamma, rho, verification rates from its own output), and adjusts behaviour based on that monitoring (metacognitive feedback protocol). Meets the formal definition in Mathematical Appendix Section 8.3. Substrate-agnostic.

### Skin Barrier

Immune pipeline front-gate filter. Pre-filters obviously malformed or garbage findings before they enter the full pipeline. Reduces processing load on downstream cells.

### Target Kind

`python` or `prose`, resolved by the harness from the target itself rather than
declared in configuration; a config declaration may veto a run on disagreement
but can never redirect it. It governs which mechanisms apply — not whether the
target is computable. Prose is fully reviewable; what changes is that file-based
Python tools (ruff, mypy, bandit) cannot read a markdown file, so they are
bypassed and reported NOT_APPLICABLE rather than run and believed.

### Stall Detector

Secondary convergence mechanism, independent from the primary gate. Checks whether open findings and contested counts have been static for a sustained window combined with gamma threshold. Two tiers: advisory (gamma at least 0.30, log only) and terminate (gamma at least 0.45, fires STALL_CONVERGED).

### Star Topology

Structured blackboard communication topology. Models interact only with the central FindingRegistry, not with each other directly. The runner owns all state. See also Blackboard.

### Substrate Agnosticism

Design principle: none of the mathematical formulas reference substrate-specific terms (model, machine, AI). Every quantity is computable from structured analytical findings regardless of source — human, machine, proprietary, open-source. Defined in Mathematical Appendix Section 8.4. Testable prediction: human teams under CDSFL will exhibit measurable decay curves.

### Substrate Ceiling

The architecture amplifies existing competence but cannot create competence from nothing. A panel of models that cannot analyse code will not produce valid code analysis regardless of the protocol.

### Two-sided gate (critical quiescence)

The runner's terminal convergence condition since the Experiment 40 arc. It fires only when both sides of the same diminishing-returns measure agree: `gamma_critical` at or above threshold (default 0.30) **AND** a run of consecutive rounds (default 3) producing no new genuine CRITICAL finding — with no unverified critical pending, nothing contested, no churn, and the irreducible queue within bound. Either side alone is insufficient. Reported in a run's `convergence_reason` as `CRITICAL_QUIESCENCE_CONVERGED (two-sided gate)`. Implemented at `bench/reference_runner_v2.py:2833-3035`; the pass condition for any given config is printed by `python3 bench/launch_exp42.py --config <config> --dry-run`.

Where the cumulative critical count over the whole run is zero, the decay curve does not exist and `gamma_critical` returns 0.0 — indistinguishable, numerically, from the worst case. That run converges on the count side alone, guarded by a requirement that the panel produced findings of some severity, and is labelled `(two-sided gate, VACUOUS CURVE)` so a reader can judge it.

### V-hat (V-hat)

Value-based termination criterion in the Mathematical Appendix. The runner's convergence gate uses a state-based approach instead. Gap 5 in the model audit: runner gate conditions do not match appendix termination criteria.

### Veto, and NO_APPLICABLE_CHECKS

A veto is a check that may only REJECT, never license a close. `ast.parse` on a
document's fenced listings is the canonical case: it is a statement about the
LISTING, never about the FIX. Every harmful fix is syntactically valid, so a clean
parse returning PASS closed a fix injecting `subprocess.call(..., shell=True)`
(measured, 2026-08-01). Verification is therefore tri-state — FAIL /
NO_APPLICABLE_CHECKS / PASS — and vetoes are recorded in `vetoes_run`, kept
separate from `checks_run`, because a veto that passes must never read as a check
that ran.

### Verification Chain

Cryptographic audit trail (`bench/verification_chain.py`). Implements RFC 9162 with hash chains, Ed25519 signing, epoch sealing, and inclusion proofs. Provides tamper-evident record of all findings and their verification status.

### Y (Cognitive Yield)

Total cognitive yield: finding count times mean abstraction depth. When findings decrease but depth increases, total yield can still rise. Captures ascending abstraction as a distinct cognitive mode. Defined in Mathematical Appendix Section 7.
