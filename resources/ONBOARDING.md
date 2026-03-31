# CDSFL Project Onboarding

Last updated: 31 March 2026

Read this document first if you are a new model instance, a new developer,
or a reviewer picking up this project for the first time.

## What This Project Is

CDSFL (Constraint-Driven Synthesis and Falsification) is a methodology for
making AI-assisted technical work more reliable. It formalises the scientific
method — specifically Popperian falsification — as a structured protocol that
AI models follow when producing and reviewing technical output.

The project is approximately 13 days old (first commit: 14 March 2026). It
was built by a single founder (George Jackson) working with Claude Opus 4.6
as primary collaborator and OpenAI Codex 5.3 as independent falsifier, with
DeepSeek V3.2, Gemini 3.1 Pro, and ChatGPT 5.4 as additional review models.

**Repository:** `github.com/jebus197/Constraint_Engineering`
**Local path:** `/Users/georgejackson/Developer_Projects/Constraint_Engineering/`

## Current State (update after each major milestone)

- **Bench Run 1:** 27 tasks x 4 conditions = 108 runs, 5 models per run.
  ~78 of 108 complete. Known confounds (BENCH_RUN_1_ANALYSIS.md). Run 2 planned.
- **Meta-test Stage 1 COMPLETE (27 March 2026):** 5-model blind pass on the
  mathematical model itself. 11 genuine fixes applied to MATHEMATICAL_APPENDIX.md
  (commit `08ccab1`). CC2 dominated (16 findings, 10 genuine, 8 unique). CX
  contaminated (read Gemini output, Δ≈1.0). ChatGPT non-compliant (format failure).
- **3-model confer COMPLETE (27 March 2026):** First fully functional distributed
  compute round. CX + Gemini + CC2, all under CDSFL system prompt, resolved 5
  deferred design decisions and added manager selection function §7.11. Commit `77a4a7f`.
- **Persistence layer BUILT (28 March 2026):** `bench/verification_chain.py` —
  790 lines, 97 tests, RFC 9162 Merkle trees, hash chains, optional Ed25519.
  Output correct. Distributed compute protocol not followed — founder chose
  efficient build over clean test. Documented as Experiment 10 (process observation).
  Protocol document written: `bench/DISTRIBUTED_COMPUTE_PROTOCOL.md`.
- **Experiment 11 Phases 1–3 COMPLETE (28 March 2026):** Five-model distributed
  compute test formalising dynamic management and load-balancing (6 areas). CC1
  collator, CC2 player manager. Phase 1: CC2 architecture + self-review (16
  revisions integrated into converged_plan.md). Phase 2: blind round — CC2,
  ChatGPT, Gemini, DeepSeek succeeded (4/5); Codex timed out (600s CLI limit).
  Phase 3: CC2 synthesis declared structural convergence in 1 round. Two SOFT
  design choices flagged for founder review. Logs: `bench/logs/experiment_11/`.
- **Experiment 12 COMPLETE (29 March 2026):** First live orchestration of
  `dynamic_management.py` (3181 lines, 27 classes) — 20 rounds, 5 models,
  809 findings. Terminated at MAX_ROUNDS (detectors broken). Three broken
  detectors diagnosed and fixed mid-run: kappa (Jaccard too strict), mu (cost
  distortion from model attrition), Gemini tau (threshold too aggressive).
  Immune response layer (DetectorHealthMonitor) added. Context windowing,
  adaptive decomposition, and novelty rate stop signal committed. Statistical
  analysis: only ChatGPT severity shows significant improvement (p=0.006).
  CC2 vocabulary novelty declined 23.9%→7.7% over 20 rounds (genuine
  diminishing returns, not churn). Fingerprint EMA collapses over 20 rounds
  (fix needed: windowed mean). Logs: `bench/logs/experiment_12/`.
- **Experiment 13a COMPLETE (29 March 2026):** Confer round — CC2 P-passed all
  8 post-Exp12 fixes under full CDSFL. 4 approved, 3 modified, 1 deferred.
  Applied: per-model restart guard, max_rounds ceiling (30), vocab monotonic-decrease
  documentation. Per-model mu implemented and wired (CC2 approved HARD).
  177 tests. Logs: `bench/logs/experiment_13a/`.
- **Experiment 13b COMPLETE (29 March 2026):** Second live orchestration
  with all fixes active. 4 rounds, 185 findings, ALL 5 models survived.
  Terminated via CONVERGED (not MAX_ROUNDS). Vocab saturation fired correctly.
  mu declined monotonically (65→15→7→0). Gemini survived all rounds (tau fix
  worked). No model restarts needed (context fixes prevented blocking).
  Vocabulary exhausted by Round 1 (2085→2113→2113 unique terms). Sharp
  convergence: Round 3 had zero novelty and zero vocab growth. Investigation
  needed: 4 rounds may be premature termination if similarity function is
  too aggressive. Logs: `bench/logs/experiment_13b/`.
- **Exp13b FULL ANALYSIS COMPLETE (29 March 2026):** 184 findings parsed and
  analysed with SymPy, Wolfram, SciPy. Per-model severity hierarchy: Gemini
  (0.818) > Codex (0.785) > ChatGPT (0.684) > CC2 (0.630) > DeepSeek (0.557).
  Kruskal-Wallis H=44.74, p<0.0001. Duane NHPP fit R²=0.9999. Models
  independently found issues in 7/8 fix areas (97 related findings). Premature
  termination diagnosed: decomposed dispatch × vocab saturation threshold
  interaction (Heaps' law). Recommended: τ 0.10→0.03-0.05, W 3→5.
  Full write-up in EXPERIMENTAL_RESULTS.md.
- **SELF-ADAPTIVE CDSFL ANALYSIS COMPLETE (29 March 2026):** P-passed three-tier
  self-adaptation architecture. Tier 1: bounded parameter adaptation via immune
  layer. Tier 2: per-model prompt adaptation via existing registry Layer 4 (TOML
  files exist, not wired). Tier 3: structural adaptation (future). Five failure
  modes falsified (oscillation, overfitting, gaming, corruption cascade,
  comparability loss). DeepSeek dual pathology identified: dispatch blocking +
  verification miscalibration (0% self-verified, 6/15 corroborated TRUE by
  peers). Three new immune layer pathology types designed (dispatch false
  positive, verification miscalibration, cross-model contradiction).
  Implementation roadmap: Phases A-E. TTS exports on Desktop.
- **Experiment 14 PLAN APPROVED (29 March 2026):** Implement self-adaptive
  fixes (Phases A–E), then run against dynamic_management.py with all 5 models
  targeting Areas 4–7 (undertested detector/immune code). Phase A: wire per-model
  registry Layer 4 into orchestrator. Phase B: close immune feedback loop
  (apply_diagnosis()). Phase C: per-model prompt adaptation (DeepSeek verification
  fix). Phase D: area-level vocabulary tracking (replaces global). Phase E:
  dispatch health monitoring (3 new pathology types). Recalibrate τ_vocab 0.10→0.04,
  W 3→5. 7 falsifiable predictions registered. Predicted termination: rounds 8–15.
- **Experiment 14 Phases A–E COMPLETE (29-30 March 2026):** Self-adaptive
  immune layer implemented. Per-model registry Layer 4 wired. Immune feedback
  loop closed (apply_diagnosis). Per-model prompt adaptation. Area-level vocab
  tracking. Dispatch health monitoring with 3 new pathology types. Recalibrated
  τ_vocab_growth 0.10→0.04, vocab_sustained_window 3→5. 234 tests.
- **Experiment 15 IN PROGRESS (30 March 2026):** Live wire run of
  `dynamic_management.py` (now ~6,100 lines) with all 5 models. Self-adaptive
  immune layer (Level 3) active. Three runs attempted: Run 1 killed by
  DeepSeek CircuitBreakerTripped, Run 2 killed by same, Run 3 in progress
  (Round 1, 21 findings so far). Fixes applied mid-experiment: circuit breaker
  catch (`aa89585`), DeepSeek CoT budget exhaustion retry with halved
  max_tokens (`5058d29`).
- **Experiment 15 failure mode analysis COMPLETE (30 March 2026):** 6 failure
  modes classified across mathematical model and immune layer. Dual-track
  fixes implemented (`df52e85`):
  - Mathematical model (MATHEMATICAL_APPENDIX.md §2): delivery feasibility
    f_del, decomposition yield bounds η_dec, format yield φ_fmt(i). Combined:
    q_ik = f_del(i) · φ_fmt(i) · d_ik · p_ik. All reduce to existing when factors=1.
  - Immune layer: 3 new detectors (parser yield anomaly, monotonic decline,
    cost-per-finding spike). [253 tests](../bench/TEST_COVERAGE.md) passing (19 new).
- **Immune persistence + Policy Engine PLANNED (30 March 2026):** JSON-based
  cross-experiment memory for immune layer (est. 150 lines). Policy Engine
  consolidation of remediation chains, registry TOML, inline heuristics.
  Deferred until Exp15/16 iteration stabilises immune layer shape. Plan:
  `docs/experimental_notes/Immune_Persistence_And_PE_Plan_2026-03-30.md`.
- **STOPPING CRITERION (founder-defined, 30 March 2026):** Everything wired
  and fully operational to the extent that the bench produces meaningful
  results without wasted compute on broken detectors, format failures, or
  premature termination. Bench Run 2 must be a legitimate scientific
  experiment, not a debugging session. We stop iterating on the methodology
  when we can show the bench produces meaningful results. Occam's razor
  applies: simplest sufficient solution at every level. The wider community
  will have far greater compute to refine further.
- **META-TRAJECTORY:** Problem space is shrinking across experiments. Exp12
  found structural failures (broken detectors). Exp13 found calibration
  errors (one threshold). Exp14 found design gaps (not broken code). Exp15
  found edge cases (format divergence, CoT budget). Each iteration finds less
  fundamental problems. The methodology is converging on itself. Experiment
  numbering must auto-increment from logs directory (currently hardcoded).
- **Experiment 15 Run 3 COMPLETE + Layer 1 fixes (30 March 2026, `148f80d`):**
  286 findings across 7 rounds (5 models). Parser fix recovered +18 findings
  (Gemini/ChatGPT tuple format). CX confer produced 7 findings, 4 applied.
  4 convergent findings from multi-model agreement resolved: ascending
  abstraction guard wired into stop(), reassign() scores persisted, recovery
  actions propagated to RoundResult, _solve_greedy() feasibility pre-check.
  Process resilience: httpx timeouts + multiprocessing watchdog. Dynamic
  experiment numbering (auto-increment). 350 tests. Experiment 17 plan
  drafted (immune + load balancing layer validation).
- **Experiment 16 COMPLETE (30 March 2026, `881cf43`):** 5-model CDSFL review
  of Exp 17 plan. 54 P-pass findings, 45 proposed improvements. 11 convergent
  themes resolved: full file delivery (not extract), split blind round (R0A+R0B),
  independent stop caps, behaviour-based success criteria, fault injection
  scenarios, mandatory telemetry, SymPy for math ops, dependency-aware fix DAG,
  DeepSeek decomposition, load balancing separate with interface contracts.
  All 4 open questions resolved. Plan status: APPROVED.
- **Experiment 17 prerequisites COMPLETE (30 March 2026, `e59f522`):**
  Runner script, 4 canary tests (empty response, false positive, cascade,
  oscillation — all passing), 5 Layer 1 preflight tests, round-level telemetry,
  DeepSeek 3-area immune decomposition, interface summary, appendix-to-code
  traceability (22 fully implemented, 5 partial, 8 not implemented formulas).
  Independent stop caps (round 10, wall-clock 4h). Ready to execute.
- **Experiment 17 CODE FIXES APPLIED + FFF CONVERGED (31 March 2026, `d85eb5a`):**
  Round 3 COMPLETE (140 findings), Round 4 partial. All applicable code fixes
  applied in 4 batches: 8 IM + 9 LB + 14 VC + 4 MM = 35 fixes. 351 tests passing.
  Three-way FFF round-robin (Gemini → CX GPT-5.4 → Gemini) under CDSFL converged
  in 3 rounds with 7 additional fixes. Key: pathology_key routing (IM_F013),
  remediation escalation reset (IM_F002), verify_chain exception safety, estimate_gamma
  correction, kappa_rate divergence fix. Logs: `bench/logs/gemini_fff_exp17_fixes/`.
- **Experiment 18 runner BUILT (30 March 2026, `e11b4a2`):**
  `bench/run_exp18_confer.py` — sequential confer architecture (Phase 1+2 of
  Whole Body Architecture). Fingerprint-based dispatch ordering (strongest model
  first, player_manager last as arbitrator). Attributed findings with
  `[source: model_id]`. Three output types: NOVEL, VALIDATION, CHALLENGE.
  Position-aware prompts (first reviewer, confer, arbitrator). Inherits
  decomposition and feasibility gate from Exp 17. Pending: preflight + canary
  test before launch. Launches after Exp 17 findings are collated and integrated.
- **Whole Body Architecture designed (30 March 2026):** Design note at
  `docs/experimental_notes/Whole_Body_Architecture_Plan_2026-03-30.md`.
  Three communication layers: nervous system (dispatch sequencing), circulatory
  system (attributed finding flow), endocrine system (adaptive pacing signals).
  Four phases — Exp 18 implements Phases 1 (attributed findings) and 2
  (sequential dispatch). Phases 3 (multi-step pacing) and 4 (closed-loop
  feedback) are future work.
- **CX prompt efficiency confer COMPLETE + IMPLEMENTED (30 March 2026, `8c1dacb`):**
  CX context waste (78 tool calls, 155K tokens). Fix: 6-field standard confer
  packet, stdin piping, `--output-schema`. 78% token reduction. ALL IMPLEMENTED
  in orchestrators. Record: `docs/experimental_notes/CX_Prompt_Efficiency_Confer_2026-03-30.md`.
- **CX efficiency confer R2 COMPLETE (31 March 2026):** CX hit usage limit after
  ~3h runtime. 4-model confer (CC2, ChatGPT, Gemini, DeepSeek) under CDSFL on
  CX dispatch costs. 2 rounds, converged. CLI audit revealed: reasoning effort
  locked at xhigh, 4 MCP servers loading per dispatch, no ephemeral mode. Fixes
  implemented in `call_codex()`: `-c 'model_reasoning_effort="medium"'`,
  `-c "mcp_servers={}"`, `-c "plugins={}"`, `--ephemeral`. Confer results:
  `bench/logs/cx_efficiency_confer_r2/`.
- **MIDCA analysis COMPLETE (31 March 2026):** CDSFL mapped against Cox et al.
  AAAI-16 MIDCA standard. 6/8 core requirements met, 2 partial (expectation
  generation, anomaly detection partially implicit). CDSFL extends beyond MIDCA
  scope in multi-agent coordination and substrate-agnostic measurement. Honest
  assessment: system-level metacognition, not agent-level. Analysis:
  `docs/experimental_notes/CDSFL_MIDCA_Analysis_2026-03-30.md`.
- **Composable directive architecture P-PASSED (31 March 2026):** Modular,
  dynamically assembled directive packets preserving core Popperian constraints.
  Four-layer stack: Universal → Domain → Phenotype → Situation. 5 falsification
  passes, 5 falsifiable questions generated. Dynamic composer (~200-400 lines)
  identified as missing piece. Proposed as Experiment 19. Analysis:
  `docs/experimental_notes/CDSFL_Composable_Directives_Analysis_2026-03-31.md`.
- **5-model composable directives confer COMPLETE (31 March 2026):** 3 rounds ×
  5 models (~191K chars). Open-format architecture review. All 5 models agreed
  on four-layer stack, phenotype-as-transform, coherence budgeting, and the need
  for a dynamic composer. Independently converged on coherence penalty, attention
  yield, and diversity decomposition. Results: `bench/logs/composable_directives_confer/`.
- **5-model composer review confer COMPLETE (31 March 2026, `adaa434`):** 2 rounds ×
  5 models (~303K chars). "Problem box" format — models constrained to produce
  working code solutions only. All 6 identified problems solved. CX won all 6.
  ChatGPT strong second. Results: `bench/logs/composer_review_confer/`.
- **Dynamic Directive Composer BUILT (31 March 2026, `adaa434`):**
  `bench/cdsfl_registry/composer.py` — 1,399 lines. Four-layer directive
  composition with monotonicity enforcement, coherence budgeting, CID provenance.
  All 6 confer fixes applied: universal minimal rendering (1,865 chars vs 9,597),
  intra-packet pruning (two-pass HARD/SOFT), 9-step phenotype transform (Jaccard
  dedup), cross-layer conflict resolution (3-rule hierarchy), coherence threshold
  calibration from experiment logs, orchestrator integration helpers. All 5 model
  compositions valid, no monotonicity violations.
- **SymPy verification of composer + mathematical model (31 March 2026):** 8
  implementation claims verified (density monotonicity, calibration threshold,
  Jaccard→containment, pruning convergence, priority total order, coherence
  detection reduction, constraint preservation, dedup threshold). 12 mathematical
  model claims verified (unified detection equation, attention yield, coherence
  penalty, correlated joint miss, diversity decomposition, Ising model with
  bounded ψ, hierarchical dependence, correlation-adjusted coverage, entropy
  coherence, composition monotonicity, critical mass sigmoid, diversity ratio).
  All pass. Ising model requires Σψ ≤ −Σlog(1−q_i).
- **TTS output protocol updated (30 March 2026):** New `tts-output-protocol`
  directive. Per-project Desktop folders (`CDSFL_tts/`, `Genesis_tts/`) + repo
  `experimental_notes/` as .md. 141 files migrated from `~/Desktop/Accessibility/`.
- **Decomposed dispatch infrastructure BUILT (31 March 2026, `d139e12`):**
  `bench/decomposed_dispatch.py` — reusable multi-turn staged context loading for
  all 5 APIs (Gemini chat, OpenRouter messages, DeepSeek messages, CX accumulated
  context). Implements the "tutor" pattern: chunks delivered with "WAITING"
  acknowledgement, synthesis triggered only after full payload received.
- **Gemini Phase 1 mathematical coherence audit COMPLETE (31 March 2026, `d139e12`):**
  8-chunk decomposed delivery (~65K chars). All 8 WAITING responses clean. 14,872
  chars of mathematical analysis (174s). Findings: 14 symbol collisions (namespace
  refactor HARD), all 5 deferred items resolved (A-D1 asymmetric Δ, A-D2 D→ρ_info,
  A-D3 keep step, A-D4 M_suppress volume constraint, A-D5 T_conv/T_budg). A-N1
  anti-parroting REJECTED (contradicts O_A). A-N3 modified (bound ascending_bonus).
  Ising model explicitly rejected. Decomposed delivery attention claim FALSIFIED
  (cumulative context). Proposed §9-§11 structure. Log:
  `bench/logs/gemini_math_audit/round0_gemini_20260331T102313Z.json`.
- **6-round mathematical coherence audit CONVERGED (31 March 2026, `0c5d7ea`+):**
  Iterative Gemini-led audit with 5-model CDSFL review and SymPy verification.
  Round 0: Gemini Phase 1 (8-chunk decomposed, 14,872 chars, 6 tasks). Round 1:
  SymPy 13/13 PASS + CC observations. Round 2: Gemini Phase 2 (namespace table,
  §9/§10 text, self-falsification). Round 4: 5-model review (CC2+CX+ChatGPT+
  DeepSeek+Gemini, 28,088 chars, consensus matrix). Round 5: SymPy 10/10 PASS.
  Round 6: Gemini final resolutions + CX verification (3 APPROVE, 2 MODIFY).
  **Resolved (8):** §9.1 P(y_t|x)=⊥→P=0, §9.2 N_len* uniqueness conditional,
  A-N1 rejection, A-N2 acceptance, §11→§9.4 fold, synthesis deferral, deferred
  items A-D1–D5, ρ_eff domain restriction [0,1]. **Outstanding (2 minor):** CX
  modifications to O2 (q_i terminology) and O4 (piecewise weight definition) —
  both editorial, not mathematical substance. Logs: `bench/logs/gemini_math_audit/`.
  **Key outcomes:** normalised Ising model with partition function Z, C(n)
  independence branching (independent vs correlated via Ising), full namespace
  refactor table (17 collisions), decomposed delivery reformulated as synthesis
  deferral operator τ_defer, A-N1 anti-parroting REJECTED, A-N3 null-vector guard.
- **Find-Fix-Follow pattern identified (31 March 2026):** Analysis of founder's
  informal Gemini interaction pattern revealed a three-step intra-model cycle
  (find issue → resolve it → explore consequences of resolution) that produces
  scope expansion beyond what inter-model confer rounds alone achieve. Currently
  CDSFL rounds require models to report findings but not to resolve them within
  their own turn. Adding a resolution-and-consequence obligation to round
  instructions would reduce rounds-to-convergence and increase cross-section
  issue discovery. Testable as Exp 19 condition or Bench Run 2 variant. Also
  identified: seeded sensitivity (known-defect injection for calibration) and
  NMI-based sycophancy trigger from same Gemini session warrant evaluation
  against existing S_sync and immune layer.
- **Round 7 find-fix-follow audit COMPLETE (31 March 2026, `e86d44e`):**
  Gemini received full 826-line appendix + all Round 6 resolutions under CDSFL
  with find-fix-follow instructions. Found 6 integration issues (namespace detail
  renames, C(n) branching placement as §0.1, τ_defer exponential penalty for
  decomposition, null-set evaluation with context indicator, suppression guard
  circular reference, separability axiom placement + ρ clipping). All fixed with
  exact text. SymPy 10/10 PASS. Gemini declared model mathematically coherent
  and complete. First practical demonstration of find-fix-follow producing
  cross-section integration findings in a single round.
- **Round 8 Gemini construct evaluation COMPLETE (31 March 2026, `e0cbb99`+):**
  9 constructs from informal founder-Gemini interaction evaluated under CDSFL
  find-fix-follow. Gemini evaluated its own earlier work against the converged
  model. **3 ADOPT:** seeded defect injection (empirical ground-truth for m_k),
  NMI diversity audit (observable estimator for d_ik and J_ij), sycophancy
  trigger via S_H (anchors S_sync to empirical observables). **3 MODIFY:**
  error re-injection rate (maps to existing Δ, adds divergence halt), HIL
  framing penalty (formalises hint damage to search space), substrate ceiling
  (asymptotic boundary on R_n). **3 REJECT:** Mayo severity (redundant with
  §4+§0.1+§7.8), calibration coefficient ω (unnecessary scalar), optimal
  stopping (§7.4 already handles). SymPy 6/6 PASS. Total audit: 8 rounds,
  39 algebra checks, all passing, 6 models examined. Model remains coherent.
  Log: `bench/logs/gemini_math_audit/round8_fff_eval_gemini_20260331T145404Z.json`.
- **MATHEMATICAL_APPENDIX.md REWRITTEN (31 March 2026, `c7f9e7a`):** All
  converged fixes from 8-round audit applied. 826 → 1022 lines. §0.1 Ising
  branching, full namespace refactor (17 collisions), τ_defer, null-vector guards,
  separability axioms, ρ clipping, seeded sensitivity Ŝ_H, NMI diversity δ_ij,
  S_sync^emp empirical anchor, error re-injection ν, HIL framing penalty IG_HIL,
  substrate ceiling. Post-edit SymPy 7/7 reduction properties confirmed.
- **Next:** Apply Exp 17 implementation fixes (IM_F001-F013, LB, VC) → wire
  composer into orchestrator → resume Exp 17 (CX resets ~3 Apr) → Exp 19
  (find-fix-follow condition) → Exp 18 → immune persistence + PE → Bench Run 2.
- **Experimental design:** 2x2 factorial — Control (no methodology),
  HIL (expert hint only), CDSFL (structure + verification), CDSFL+HIL (full
  methodology with expert guidance and research)
- **System prompt injection:** `run_benchmark.py` (lines 310-673) implements
  correct per-model system prompt delivery for all 5 models. Use this
  infrastructure — do not reinvent.
- **Verification:** SymPy (OSS) auto-verifies mathematical claims. CC
  extracts verifiable claims from raw findings when models don't provide them.
- **Policy engine:** Hierarchical Constraint Editor (CE) with 5 layers:
  universal, domain, task, model, runtime.
- **Domain expert configs:** First configs produced — portable, three-layer
  (methodology + domain + personalisation). See `configs/`.

## Smoke Test Results (24 March 2026)

The corrected experimental design produced:
- Control: 10 unique HARD findings (5 rounds self-iteration)
- HIL: 2 unique HARD findings (5 rounds self-iteration)
- CDSFL: 29 unique HARD findings (5 rounds confer)
- CDSFL+HIL: 43 unique HARD findings (5 rounds confer)

Gradient: HIL (2) < Control (10) < CDSFL (29) < CDSFL+HIL (43)

## Architecture Overview

```
Constraint_Engineering/
  PAPER.md                    -- Canonical technical statement (white paper)
  README.md                   -- Operational front door
  configs/                    -- Domain expert configurations (tradeable assets)
    examples/                 -- Methodology, software engineering, template
  docs/
    FOUNDERS_NOTES.md         -- Chronological design observations
    EXPERIMENTAL_RESULTS.md   -- All experimental data including failures
    EXTENDED_RATIONALE.md     -- General-audience companion
    MATHEMATICAL_APPENDIX.md  -- Mathematical extensions
  bench/
    run_round_robin.py        -- Main bench test orchestrator (~3500 lines)
    run_exp17_immune.py       -- Exp 17: immune + LB live validation runner
    run_exp18_confer.py       -- Exp 18: sequential confer runner (Whole Body)
    cdsfl_registry/           -- Constraint Editor (CE) policy engine
      registry.py             -- 5-layer hierarchical merge with monotonicity
      composer.py             -- Dynamic Directive Composer (4-layer composition)
      refinements.py          -- Independence-aware confirmation, tuple canon
      universal.toml          -- Layer 1 (immutable HARD constraints)
      domains/                -- Layer 2 (domain-specific policies)
      models/                 -- Layer 4 (model-specific settings)
    tasks_frontier/           -- 27 frontier tasks (ft-001 through ft-027)
    directives/               -- Domain-specific constraint boxes
    interactive_smoke.py      -- Bidirectional P-pass test script
    tutor_test.py             -- Tutor-style decomposition test
  resources/                  -- This folder — onboarding and recovery
```

## Key Concepts

**P-Pass:** Popperian falsification pass. Generate, attack, fix, repeat until
diminishing returns. The core mechanism.

**HARD/SOFT classification:** Constraints classified as non-negotiable (HARD)
or preference-based (SOFT). Ambiguous defaults to HARD.

**Confer/Defer:** Multi-model protocol. Models review each other's findings
iteratively. Confer = agreement. Defer = escalation to human review.

**Decay curve (D):** Genuine analysis produces diminishing finding rates per
round (Duane NHPP model, γ > 0). Chatbot churn produces flat curves (γ ≈ 0).
The shape distinguishes analysis from noise.

**(D, v-bar, A, C) fingerprint:** Four-metric capability assessment.
D = decay rate, v-bar = verification score (SymPy-confirmed fraction),
A = total verified findings, C = coverage of constraint space.

**Abstraction Index H(x):** Measures finding depth — formality × information
density × generalisation scope. Captures the difference between spotting a
typo and identifying a paradigm-level architectural flaw.

**Total Cognitive Yield Y(t):** Count × mean depth. When findings decrease
but depth increases, total yield can still rise. Captures ascending
abstraction as a distinct cognitive mode.

**Emergence:** When multiple agents work under structured falsification,
the composite system's Y exceeds any individual's. Empirically demonstrated
in the three-architecture review (Gemini found 16 issues CC/CX missed).
Formalised in Mathematical Appendix §8.

**Second-order cognition:** The composite system analyses, monitors its own
analysis (via decay curves + verification rates + adoption deltas), and
adjusts based on monitoring (metacognitive feedback protocol). Meets the
formal MIDCA definition. Substrate-agnostic — the same maths applies to
human teams.

**Constraint Editor (CE):** Hierarchical policy engine. 5 layers cascade
with monotonicity — lower layers cannot weaken higher-layer HARD constraints.

**Domain expert config:** Portable cognitive encoding with three layers:
universal methodology, domain-specific directives, user personalisation.

## Known Confounds (document honestly)

1. **Directive asymmetry:** CC and CX carry the founder's cognitive
   methodology directives (CLAUDE.md) into all conditions. DeepSeek, Gemini,
   and ChatGPT operate with no equivalent. This affects between-model
   comparisons but not between-condition comparisons.

2. **ChatGPT context overflow:** ChatGPT via pipe mode accumulates full
   conversation history. 24 warnings, 1 failure in bench test. Context cap
   not yet applied to ChatGPT (applied to CX only).

3. **SymPy extraction gap:** CC extracts mathematical claims from raw
   findings when models don't include verifiable_claim fields. Extraction
   quality varies — some claims are unparseable by SymPy. The natural
   language mathematical interpretation gap is a known limitation.

4. **Small model population:** 5 frontier models from 4 vendors is the
   available population, not a chosen sample. The diversity hypothesis
   cannot be fully tested until the ecosystem is larger.

5. **HIL prompt narrowing:** The HIL guidance says "focus on these points,"
   which narrows model search. Confirmed by framing bias literature
   (arXiv:2603.18740). Fix designed: iterative 5-round guidance pattern.

6. **ChatGPT hidden system prompt:** ChatGPT 5.4 via proprietary API carries
   a hidden RLHF preamble. Fix designed: OpenRouter access with user-defined
   system prompts.

7. **Phantom HARD inflation:** Default constraint_class was HARD instead of
   SOFT. Fixed in code but affects Run 1 data.

## Communication Protocols

The founder uses single-token shorthand to steer cognitive mode. Commands
compose left-to-right, separated by a single space. Full reference:
`resources/SHORTCUTS.md`.

- `y` = yes/approved
- `cy` = continue
- `rt` = read context files + continue
- `d` = discuss before proceeding
- `r` = re-read key context files (IM, checkpoints)
- `p` = P-pass (Popperian falsification — iterative, not observational)
- `c` = confer with all available models under CDSFL protocol
- `a` = analyse dispassionately
- `e` = extrapolate beyond immediate domain
- `rr` = full recovery (rebuild context from all sources)
- `rs` = restore state (IM + OB + checkpoints + memory)
- `t` = send to TTS (accessible plain-text export)
- `sv` = save state (Open Brain + update docs + commit + push)
- `re` = external research (web search, arXiv, Semantic Scholar)
- `g` = confer with Gemini specifically
- `sy` = check with SymPy (mathematical verification)
- `x` = override sleep/rest warnings for current session
- `qc` = quality control (full docs/staleness/consistency check)

These compose: `p d e` = falsify, discuss, extrapolate. `rs qc` = restore
state, then quality control.

## How to Resume Work

1. Read this document
2. Check `git log --oneline -10` for recent commits
3. Check if bench test is running: `ps aux | grep run_round_robin`
4. Read latest log: `tail -30 bench/logs/$(ls -t bench/logs/ | head -1)`
5. Check MEMORY.md for persistent project state (if available)
6. Read FOUNDERS_NOTES.md for design intent and open questions

## How to Reproduce Results

```bash
cd bench
pip install -r requirements.txt
source ../.env    # API keys for DeepSeek, Gemini, OpenAI, Wolfram
python3 run_round_robin.py --phase2 --smoke --tasks ft-001   # single task smoke test
python3 run_round_robin.py --phase2                           # full 26-task bench
```

All results are checkpointed. Use `--resume` to continue after interruption.

## How to Refute Results

Run the bench test yourself. Compare your (D, v-bar, A, C) fingerprints
against the published results. If your Control condition outperforms your
CDSFL+HIL condition, the methodology fails on your tasks. Publish the result.
That is data, not failure.
