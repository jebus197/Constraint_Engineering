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

Claude Code Opus 4.6 running in UX (interactive) mode. The operator instance — runs the conversation, coordinates work. Not a panel participant. Uses the Max subscription.

### CC2

Claude Code Opus 4.6 running in piped mode (`claude -p`). Headless CLI instance dispatched via the Claude binary. Used as verification agent (CC2v) in runners and available for confer. Same Max subscription as CC1.

### CC2v

CC2 verification agent. Runs between rounds in the experiment runners. P-passes OPEN findings that the immune pipeline cannot mechanically verify. Produces structured verdicts: CONFIRM, REJECT, DUPLICATE, ESCALATE. Confidence-gated at 0.7. Activates from round 6.

### CDSFL

Constraint-Driven Synthesis and Falsification. The protocol-level architecture for scientific cognition that this project implements. Formalises Popperian falsification as a structured protocol for multi-model analytical collaboration.

### C(H,E)

Popper's degree of corroboration. Measures how well evidence E supports hypothesis H given background knowledge. Used in the runner to track overall corroboration of findings. Defined in the white paper Section 2.1.

### Composer

The directive composition system (`bench/cdsfl_registry/composer.py`). Produces per-model phenotype-transformed versions of CDSFL directives. Each model receives the same underlying constraints but formatted for its processing characteristics (length caps, format density, stripping levels).

### Confer/Defer

Multi-model protocol. Confer: models review each other's findings iteratively, seeking convergence. Defer: escalation to HIL when models cannot resolve a disagreement. The confer protocol forces agents into analytical territory none explored alone.

### Convergence Gate

Primary termination mechanism. Five boolean conditions evaluated per round, tracked in gate_history. Fires when all five conditions are simultaneously true for a sustained window. Conditions include gamma threshold, open findings stability, inter-rater agreement, and others. Defined in topology spec T4.

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

### HARD/SOFT Classification

Constraints classified as non-negotiable (HARD) or preference-based (SOFT). HARD constraints include physics, mathematics, law, safety, and explicit absolutes. SOFT constraints include economic, preference, and convenience. Ambiguous defaults to HARD.

### HIL (Human-in-the-Loop)

Founder review. Findings escalated to HIL when models cannot resolve disagreements, when CC2v assigns ESCALATE verdict, or when contested findings persist beyond threshold. HIL decisions are final within the experiment scope.

### HT Cell (Helper T Cell)

Immune pipeline cell type. Duplicate detection. HT v2 flags approximate duplicates per round using similarity matching. Helps reduce churn by identifying when models are re-describing known issues.

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

Experiment-specific Python script that orchestrates a multi-model analysis session. Each experiment has its own runner (e.g. `run_exp36_evidence.py`) that configures topology, target file, round budget, and extension rules. All runners share infrastructure from `runner_core.py` and `experiment_11_orchestrator.py`.

### Second-Order Cognition

System that analyses problems (first-order), monitors its own analytical performance (computes gamma, rho, verification rates from its own output), and adjusts behaviour based on that monitoring (metacognitive feedback protocol). Meets the formal definition in Mathematical Appendix Section 8.3. Substrate-agnostic.

### Skin Barrier

Immune pipeline front-gate filter. Pre-filters obviously malformed or garbage findings before they enter the full pipeline. Reduces processing load on downstream cells.

### Stall Detector

Secondary convergence mechanism, independent from the primary gate. Checks whether open findings and contested counts have been static for a sustained window combined with gamma threshold. Two tiers: advisory (gamma at least 0.30, log only) and terminate (gamma at least 0.45, fires STALL_CONVERGED).

### Star Topology

Structured blackboard communication topology. Models interact only with the central FindingRegistry, not with each other directly. The runner owns all state. See also Blackboard.

### Substrate Agnosticism

Design principle: none of the mathematical formulas reference substrate-specific terms (model, machine, AI). Every quantity is computable from structured analytical findings regardless of source — human, machine, proprietary, open-source. Defined in Mathematical Appendix Section 8.4. Testable prediction: human teams under CDSFL will exhibit measurable decay curves.

### Substrate Ceiling

The architecture amplifies existing competence but cannot create competence from nothing. A panel of models that cannot analyse code will not produce valid code analysis regardless of the protocol.

### V-hat (V-hat)

Value-based termination criterion in the Mathematical Appendix. The runner's convergence gate uses a state-based approach instead. Gap 5 in the model audit: runner gate conditions do not match appendix termination criteria.

### Verification Chain

Cryptographic audit trail (`bench/verification_chain.py`). Implements RFC 9162 with hash chains, Ed25519 signing, epoch sealing, and inclusion proofs. Provides tamper-evident record of all findings and their verification status.

### Y (Cognitive Yield)

Total cognitive yield: finding count times mean abstraction depth. When findings decrease but depth increases, total yield can still rise. Captures ascending abstraction as a distinct cognitive mode. Defined in Mathematical Appendix Section 7.
