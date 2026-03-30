# CDSFL Project Onboarding

Last updated: 30 March 2026

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
    f_del, decomposition yield bounds η_dec, format yield φ_i. Combined:
    q_ik = f_del · φ_i · d_ik · p_ik. All reduce to existing when factors=1.
  - Immune layer: 3 new detectors (parser yield anomaly, monotonic decline,
    cost-per-finding spike). [253 tests](../bench/TEST_COVERAGE.md) passing (19 new).
- **Immune persistence + Policy Engine PLANNED (30 March 2026):** JSON-based
  cross-experiment memory for immune layer (est. 150 lines). Policy Engine
  consolidation of remediation chains, registry TOML, inline heuristics.
  Deferred until Exp15/16 iteration stabilises immune layer shape. Plan:
  `docs/experimental_notes/Immune_Persistence_And_PE_Plan_2026-03-30.txt`.
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
- **Next:** Experiment 17 (execute validated plan against immune layer). Then:
  immune persistence + PE. Then: Bench Run 2. Deferred math model items
  (A-D1–D5) remain open but are not blocking the bench.
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
    cdsfl_registry/           -- Constraint Editor (CE) policy engine
      registry.py             -- 5-layer hierarchical merge with monotonicity
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

The founder uses single-letter shorthand:
- `y` = yes/approved
- `cy` = continue
- `t` = export to TTS accessibility file
- `d` = discuss before proceeding
- `p` = run P-pass (falsify)
- `e` = extrapolate beyond immediate domain
- `c` = confer with CX via CLI, run mutual P-passes until convergence
- `a` = analyse dispassionately
- `r` = read IM only (quick context check)
- `rr` = full recovery (re-read all resources, rebuild context from scratch)
- `rs` = restore state (full recovery: rebuild context from all sources)
- `re` = external research (web search, arXiv, Semantic Scholar, Sci-Hub)
- `sv` = save state (Open Brain + update recovery resources + commit + push)

These compose: `p d e` = falsify, discuss, extrapolate. `c p a d` = confer
with CX, P-pass, analyse, discuss.

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
