# CDSFL Project Onboarding

Last updated: 6 April 2026 04:32 BST

Read this document first if you are a new model instance, a new developer,
or a reviewer picking up this project for the first time.

## What This Project Is

CDSFL (Constraint-Driven Synthesis and Falsification) is a methodology for
making AI-assisted technical work more reliable. It formalises the scientific
method — specifically Popperian falsification — as a structured protocol that
AI models follow when producing and reviewing technical output.

The project began on 12 March 2026 (first commit). It
was built by a single founder (George Jackson) working with Claude Opus 4.6
as primary collaborator and OpenAI Codex 5.3 as independent falsifier, with
DeepSeek V3.2, Gemini 3.1 Pro, and ChatGPT 5.4 as additional review models.

**Repository:** `github.com/jebus197/Constraint_Engineering`
**Local path:** `/Users/georgejackson/Developer_Projects/Constraint_Engineering/`

## Current State (update after each major milestone)

- **EXP 29 COMPLETE (4 April 2026, 21:43 BST):**
  First full integration test of CDSFL persistence layer with insect brain
  as central relay. 9 rounds, 340 findings, 35 min wall clock. **CONVERGED**
  at R8 (κ=0.960). C(H,E)=0.899 — highest recorded. γ=0.385 (computed).
  All 5 models survived to completion (CC2=97, DeepSeek=81, Codex=59,
  ChatGPT=57, Gemini=46). Conversational relay mode + FFF interaction pattern.
  **vs Run 10 (best baseline):** +43% findings, +0.010 C(H,E), +25% gamma,
  -5% wall clock. CC2 output +169% (36→97), Gemini +130% (20→46). Model
  spread compressed from 3.3× to 2.1×. Conversational relay is a clear win.
  **Cross-model engagement:** Gemini and CC2 produced substantive cross-model
  citations (RFC-grounded falsification, multi-model positioning). ChatGPT
  never referenced another model. Engagement intermittent, not default.
  **Bugs fixed during run:** (1) DeepSeek empty response killed experiment —
  changed to per-model benching; (2) resume directory mismatch — added
  checkpoint discovery logic.
  **New code:** `bench/run_exp29_persistence.py` (runner), interaction pattern
  presets in `bench/cdsfl_registry/composer.py`, conversational relay mode in
  `bench/insect_brain.py`.
  **Known issues for next run:** stale `anthropic/claude-haiku` model ID in
  immune shadow classifier, NK v2 doesn't set TriagedFinding duplicate fields,
  `run_immune_pipeline` discards NK v2 returned state, stale shadow docstrings.
  Logs: `bench/logs/exp29_persistence_20260404T193154Z/`.
  TTS: `~/Desktop/CDSFL_tts/Exp29_Results_2026-04-04.txt`.
- **EXP 30 COMPLETE (5 April 2026, 02:43 BST):**
  Endocrine layer + directed inter-model messaging integration test.
  15 rounds, 378 findings, 87 min wall clock. Terminated at max_rounds
  (not epistemic convergence). γ=0.320, C(H,E)=0.853.
  **Per model:** CC2=114, DeepSeek=103, Gemini=68, ChatGPT=51, Codex=42.
  **Directed messaging:** 126 messages total. ChatGPT sent 44 (vs ZERO
  cross-model references in Exp 29). CC2 sent 56. Engagement gap eliminated.
  **Endocrine layer:** 14 health cycles, 18 diagnostics each (5 security,
  4 dead_code, 4 type_safety, 3 null_deref, 2 style). Stable throughout.
  Fix evaluation sandbox operational. Pacing signals functional.
  **Hot fixes during run:** (1) endocrine pacing crash — context_budget
  passed as dict instead of int, fixed in both runner and endocrine.py;
  (2) directed message accumulation — added round windowing + truncation;
  (3) JSON parser — now iterates all JSON arrays in response, skipping
  non-findings arrays (Codex wraps in multi-array JSON); (4) double-prefix
  fix — models pre-prefixing finding IDs no longer get doubled;
  (5) classifier model ID — updated to `anthropic/claude-3.5-haiku` (floating).
  **Key finding from models:** convergence/budget-exhaustion conflation —
  max_rounds termination should not set converged=True. Multiple models
  independently proposed BUDGET_EXHAUSTED status enum.
  **vs Exp 29:** +11% findings (378 vs 340), +67% rounds (15 vs 9),
  directed messaging produced sustained novelty (R13=37 findings, 2nd highest).
  Logs: `bench/logs/exp30_endocrine_20260404T235135Z/`.
  Report: `bench/logs/exp30_endocrine_20260404T235135Z/exp30_report.json`.
  **Next:** Run Exp 31 with all fixes applied, then Bench Run 2.
- **EXP 30 POST-ANALYSIS AND FIX APPLICATION (5 April 2026, 04:47 BST):**
  Deep analysis of non-convergence in Exp 30 revealed three causes:
  (1) κ_rate instability from directed messaging sustaining genuine novelty;
  (2) finding ID collision (Gemini/DeepSeek reset IDs each round);
  (3) 62 parser garbage findings from old JSON parser.
  Root cause of excessive findings: **fix-level churn** — 232 proposed fixes
  for ~83 distinct bugs. Models endlessly debating alternative solutions for
  already-known bugs instead of finding new ones.
  **Architectural fixes applied:**
  (a) Bug-closed gate in NK cell v1+v2 — first programmatically verified fix
  wins, bug closed, subsequent findings about same bug rejected on sight;
  (b) Programmatic fix evaluation wired into immune pipeline Stage 4 —
  evaluate_fix() runs pyright/ruff/bandit/pytest in sandbox, SAFE = verified;
  (c) BUDGET_EXHAUSTED status — max_rounds no longer sets converged=True;
  (d) Context formatting shows CLOSED/PENDING/OPEN bug status to models.
  **Bug fixes from Exp 30 findings (39 total across 3 files):**
  immune_agents.py (18): log-odds sign, Z3 verification, SMT-LIB negation,
  CLI thread lock, reconciliation margin, skin barrier (3 fixes), NK v1
  control flow, sympy regex, dendritic AND join, barrier rejection counting,
  autoimmune override, dead code, lazy discovery sync, AST caching,
  statistical claims, tool_usage counting.
  insect_brain.py (10): checkpoint recovery context amnesia, immune_response
  serialisation, gamma_hat div-by-zero, handle_model_failure checkpoint,
  signal_complete atomic write + BUDGET_EXHAUSTED, exception specificity,
  max_rounds=0 guard, truncation marker, docstring, newline handling.
  verification_chain.py (8): epoch ordering/monotonicity, orphan epoch check,
  CLI/API contract alignment, seal_epoch idempotency + fsync, deep copy
  properties, load_json validation, sub-second timestamps, error truncation.
  Plus 3 architectural changes (bug-closed gate, fix evaluation, BUDGET_EXHAUSTED).
  **Tests:** 571 passed, 0 failed.
- **EXP 31 COMPLETE (5 April 2026, 07:38 BST):**
  Post-fix validation run. Same 3 test articles, same 5 models, directed relay,
  FFF pattern. Base prompt informed models of 39 applied fixes — do NOT rediscover.
  15 rounds, 360 findings, ~190 min wall clock. **BUDGET_EXHAUSTED(15).**
  Final κ=0.619, γ=0.106. All 5 models active throughout.
  **Per model:** CC2=95, Codex=85, DeepSeek=69, Gemini=61, ChatGPT=50.
  **Convergence trajectory:** γ rose from 0.000→0.063 (R0–R6), then accelerated
  to 0.115 (R7–R12) after mid-experiment interventions, before flattening at
  0.106 terminal. Opposite direction to Exp 30 (0.567→0.320, diverging).
  **Mid-experiment fixes:** (1) check_convergence() ordering — convergence
  detector before budget hard-stop; (2) signal_complete() precedence — FAILED
  before BUDGET_EXHAUSTED; (3) check_convergence() fail-fast for failed state;
  (4) B-Cell UNCERTAIN→HIL escalation (Stage 5.5); (5) Good Enough instruction
  (AGREE/CHALLENGE/EXTEND); (6) Finding merge instruction; (7) Merkle sealing.
  **18 findings catalogued (E31-01 through E31-18).** Critical: deep-copy
  propagation severs verified/escalated flags (sev 0.95), autoimmune override
  violates reconciliation lock (sev 0.90). 3 fixed during session, 11 queued.
  **Late-round discoveries (R8–R14):** AST negative literal extraction, skin
  barrier path containment gap, search manifest dict parsing, epoch schema
  validation.
  **Why convergence failed:** bug-closed gate is dead code (deep-copy issue
  severs verified flag propagation). Models reached inter-rater agreement
  (κ=0.619) but couldn't close findings between rounds.
  **Merkle sealed:** 108 records per experiment, both chains verified.
  Logs: `bench/logs/exp31_postfix_20260405T041753Z/`.
  **Post-analysis (09:12 BST):** Deep data mining revealed 6 structural
  blockers — autoimmune override, finding ID reuse, deep-copy propagation,
  FFF ordering 100% wrong, zero CHALLENGE verdicts, low comms efficiency.
  All methodology fixes applied to runners (commit 587fbe8). Exp 32 runner
  built: meta-experiment on convergence prediction and experimental design.
  Full audit complete: 13/18 verified (3 refuted, 2 partial). All 11
  verified fixes applied (commit 32ed658). 572 tests pass. Bug-closed
  gate now functional. Autoimmune respects reconciliation locks.
  Findings: `experimental_notes/Exp31_Interim_Findings_2026-04-05.md`.
  TTS: `~/Desktop/CDSFL_tts/Exp31_Final_Findings_2026-04-05.txt`.
  **Next:** Exp 32 meta-experiment, then Exp 33 endocrine layer review.
- **EXP 32 COMPLETE (5 April 2026, 10:26 BST):**
  Meta-experiment: 5 models analysed convergence data from Exp 30/31 over
  10 rounds (4 phases). 200 findings, 29 min, BUDGET_EXHAUSTED(10).
  **Unanimous verdict:** convergence occurred in Exp 31 but 5 catastrophic
  instrumentation failures prevented detection (E31-01, 02, 05, 06, 13).
  **4/5 consensus on design parameters** — star/blackboard topology,
  state-based convergence gate, CC2 multi-agent, structured verdicts.
  **PARTIAL CONFOUND:** anchoring framing ("evaluate HIL's claim that
  convergence occurred") biased models toward optimising for convergence.
  Models self-servingly recommended fewer models (3), fewer rounds (8-10),
  and demoting gamma — all reducing the ability to falsify convergence.
  **Founder overrides:** 5 models retained (diversity), 21 rounds
  (mathematical model), scale-dependent gamma (telemetry→soft→hard gate).
  Per-model: ChatGPT=55, Codex=54, CC2=42, Gemini=29, DeepSeek=20.
  Final γ=0.021, κ=0.309. Methodological finding: prompt framing is a
  confounding variable in multi-model panels.
  Logs: `bench/logs/exp32_meta_20260405T085629Z/`.
  Results: `experimental_notes/Exp32_Results_2026-04-05.md`.
  TTS: `~/Desktop/CDSFL_tts/Exp32_Results_2026-04-05.txt`.
  **Post-Exp 32 fixes:** E31-14 truncation marker attribution fixed,
  LLM classifier shadow disabled (OpenRouter → use CLI Haiku). 572 tests pass.
- **CDSFL TOPOLOGY SPEC (5 April 2026):**
  New formal specification: `bench/directives/universal/cdsfl_topology_formal.md`.
  8 sections (T1-T8) formalising the multi-model protocol: star/blackboard
  topology, finding status model (OPEN/CONFIRMED/CONTESTED/MERGED/UNCONFIRMED),
  merge contract, convergence gate, gamma estimation, round taxonomy, durability
  contract, P-pass boundary tracing. Core directives amended with boundary
  tracing. Derived from runner fitness confer (CX + Gemini, 11 bugs, 1 FP).
- **EXP 34 COMPLETE (6 April 2026, 04:17 BST):**
  Endocrine.py code review under star/blackboard topology. 5 models.
  24 rounds (extended from 21), 390 total findings, 81 canonical entries,
  58 CONFIRMED, 8 OPEN, 2→7 CONTESTED. Elapsed: 6277s (~105 min).
  γ final: 0.713 (strong depletion, hard gate passed). C(H,E): 0.7808.
  Brain signal: **INCOMPLETE** — convergence gate never passed.
  Per model: ChatGPT=144, Codex=109, CC2=60, DeepSeek=40, Gemini=37.
  **Convergence analysis:** γ plateaued at 0.754-0.758 from R12-R15
  (substantive convergence), then eroded to 0.713 as late-round model
  inflation added unmerged duplicates. Gate closest to passing at R14
  (open_ch=1, contested=2). Post-R14 divergence: open_ch rose 1→8,
  contested 2→7. Positive feedback loop — more rounds produced more
  bookkeeping debris, pushing gate further from passing.
  **Two instrumentation failures prevented gate detection:**
  (1) Verdict regex: CC2 wraps verdicts in `**bold**` markdown. Parser
  regex `(?:[-*]\s*)?` doesn't match `**MERGE C0064 <- C0008**`. Zero
  CC2 merges/confirms parsed in 24 rounds. Fixed in Exp 35 runner.
  (2) CONTESTED resolution: no path from CONTESTED→DROPPED for findings
  challenged repeatedly with zero defence. False positives (C0023, C0039
  — mypy regex) permanently block gate. Design gap identified.
  **Fix production:** 70/81 (86%) findings have proposed fixes. 61 contain
  executable Python code. Per model: ChatGPT 93%, Codex 92%, CC2/DeepSeek
  82%, Gemini 83%. Avg fix length 300-470 chars with concrete patches.
  **Fix verification: BROKEN.** 0/348 verified through immune shadow.
  342 UNEVALUABLE — sandbox missing project config, dead test paths,
  environment asymmetry. Endocrine health trend flat across all 21 rounds.
  Models diagnosed exactly the bugs that prevent their own fixes from
  being verified. Endocrine fix pipeline is dead code in practice.
  **Three dispatch bugs fixed during launch** (all 4 runners: 33/34/35/36):
  (1) compose_for_model() wrong call signature; (2) DecomposedChunk()
  text= vs content=; (3) decomposed_dispatch() mc= vs individual params.
  DeepSeek context overflow on 225K (capability-blind dispatch).
  Logs: `bench/logs/exp34_endocrine_20260405T225218Z/`.
  Report: `bench/logs/exp34_endocrine_20260405T225218Z/exp34_report.json`.
- **EXP 35 RUNNER: DUAL TOPOLOGY (6 April 2026):**
  `bench/run_exp35_policy_engine.py` rewritten with dual-topology support:
  `--topology relay|star` CLI switch. User-configurable, defaults to relay.
  **Relay mode:** Models chat through insect brain, see each other's reasoning.
  Three sub-modes: findings, conversational, directed. Budget-aware content
  sizing via brain's relay() method. Human-readable conversation logs.
  **Star mode:** Structured blackboard registry, models see only registry
  summary. Existing Exp 34 pattern.
  **Shared infrastructure (both topologies):** FindingRegistry, convergence
  gate, immune pipeline, endocrine, verification chain.
  **New modules:** ITC adaptive recovery (classify failure → adapt scope,
  never bench models), persistent signed fingerprints (load/save per-model
  capability profiles across experiments), fixed verdict regex for CC2
  bold formatting.
  **Pending:** CX + Gemini review under full CDSFL before running.
  Logs: `bench/logs/exp34_endocrine_20260405T225218Z/`.
- **EXP 35 PLAN (6 April 2026):**
  `bench/EXP35_PLAN.md` — capability-aware dispatch for PolicyEngine review.
  Budget-aware prompt builder, section map, ITC adaptive recovery,
  persistent signed fingerprints (Merkle-sealed), immune pipeline activation.
  ~225 lines estimated. Depends on Exp 34 lessons learned.
- **EXP 35/36 RUNNERS (5 April 2026):**
  PolicyEngine and evidence layer runners. Same bug fixes applied.
  Star/blackboard topology. Ready to run after Exp 34.
- **EXP 33 RUNNER BUILT (5 April 2026, 11:26 BST):**
  First star/blackboard topology experiment. Target: endocrine.py (4th file,
  never reviewed). 21 rounds (extension to 24). All 5 models retained.
  FindingRegistry class implements canonical blackboard. FFF prompt-only
  (no enforcement). State-based convergence gate (earliest R12) +
  scale-dependent gamma. Runner: `bench/run_exp33_endocrine.py`.
- **Run 11 COMPLETE (4 April 2026, 01:59 BST) = Exp 28b:**
  2 rounds, 59 findings, 42 min. **Fastest convergence in bench history.**
  γ_novel=0.737 (threshold 0.5), C(H,E)=0.873. R0: 44 findings (5 models),
  R1: 15 findings (4 models — CC2 failed dispatch). 67% immune rejection in R1.
  Three factors behind rapid convergence: (1) CC2 dispatch failure — 21 min of
  timeouts, zero R1 findings from strongest model (A=1.48); (2) aggressive NK
  dedup — 10/15 R1 findings classified DUPLICATE (tau_sim=0.33); (3) Gemini
  benched — Ω<0.1 for 2 rounds. Monolithic delivery is the bottleneck.
  **Shadow v2 first production data:** NK v2 caught 9 intra-round duplicates
  in R0 (v1 missed all 9, inflating count from ~35 to 44). B-Cell v2 ran 42
  AST-grounded SMT-LIB checks. NK v1/v2 agreed on all 10 R1 duplicates.
  Helper T v2 hybrid (log-odds within domain, max-signal across) logged
  comparison data. All v2 shadows fired correctly.
  **Convergence assessment:** Probably real but accelerated. CC2 absence and
  Gemini benching are confounds. The CDSFL/FFF Gemini review (13 findings,
  12 rounds, same code) vs Run 11 Gemini (6 findings, benched) directly
  demonstrates constraint box vs monolithic delivery.
  Logs: `bench/logs/baseline_confer_run11_20260404/`.
  Analysis: `experimental_notes/Run11_Rapid_Convergence_Analysis_2026-04-04.md`.
  **CC2 dispatch diagnosis:** Root cause identified — 300s Python subprocess
  timeout killing CC2 before completion (not a CLI limit). Three-layer fix:
  (1) increase timeout to 900s (immediate, free); (2) cell-level decomposition
  for adaptive rounds; (3) parallel split for blind rounds. All Max-funded.
  Diagnosis: `experimental_notes/CC2_Dispatch_Diagnosis_2026-04-04.md`.
  **Exp 29 strategic direction:** First integration test of target architecture,
  not another calibration run. No blind round — full conversational mode with
  insect brain relay, v2 immune activation, persistence layer, adaptive layer.
  Sequence: (1) integrate Run 11 findings, (2) activate v2 immune components,
  (3) build insect brain, (4) run Gemini HIL comparison, (5) Bench Run 2
  (27 frontier STEM problems). Endocrine system (pacing signals) designed but
  not blocking. Unified numbering (Run N → Exp N) pending.
- **HIL COMPARISON EXPERIMENTS COMPLETE (4 April 2026, 04:45 BST):**
  C1 (Realistic HIL, 5 rounds): 25 findings, 9/9 verified, 0 FP — breadth.
  C4 (CDSFL+Meta structured, 4 cells×4 rounds): 16 survivors (12 retracted
  by self-falsification), 16/16 verified, 0 FP — depth.
  Combined: ~33 unique verified findings (+32% vs best single condition).
  Overlap only ~5 findings. Cross-component bugs (C1) vs formal proofs (C4).
  **THREE-LAYER SCHEMA DISCOVERY:** (1) Meta structured prompting = reasoning
  format, (2) CDSFL constraints (FFF, falsification) = rules of engagement,
  (3) Full conversational mode = default session architecture, ITC = fallback
  only for model failure/context degradation.
  Logs: `bench/logs/hil_comparison_c1_20260404/`, `bench/logs/hil_comparison_c4_20260404/`.
  Analysis: `experimental_notes/HIL_Comparison_Analysis_2026-04-04.md`.
- **C5 THREE-LAYER SCHEMA VALIDATION (4 April 2026, 06:16 BST):**
  Full continued conversation + CDSFL system prompt + Meta structured prompting.
  8 rounds, 11.6 min, 91,731 chars output. NO ITC trigger — model sustained
  quality across all rounds. 27 consolidated findings covering 36/40 registry
  bugs + 6 wholly novel. 3 self-retractions (one corrected MF-28 as false).
  5 cross-component findings (C4 found 0). 5 novel constructs proposed.
  100% of findings include fixes (PATCH/NOVEL CONSTRUCT/ARCHITECTURAL).
  90% prior confirmation rate. 0 false positives.
  Automated verdict: PARTIAL (27 IDs vs 30 threshold — consolidation artifact).
  Qualitative assessment: combines C1 breadth + C4 depth as predicted.
  Key novel findings: path traversal file read, empty string bypass, prompt
  injection via descriptions, Confident Hallucination Highway (3-bug cascade).
  Key novel constructs: Epistemic Routing Layer, Reconciliation Gate,
  Formalisation Agent, typed LLM classifier, lazy tool discovery.
  MF-28 (regex empty string) likely false positive in registry — C5 retracted
  with valid proof.
  Scripts: `bench/c5_three_layer_schema.py`, `bench/c5_prompts.py`, `bench/c5_verify.py`.
  Logs: `bench/logs/c5_20260404T050417Z/`.
  Master Finding Registry: `experimental_notes/Master_Finding_Registry_2026-04-04.md`.
- **Run 10 COMPLETE (3 April 2026, 16:44 BST) = Exp 28:**
  7 rounds, 237 findings, 37 min. First natural convergence
  (DM kappa=1.0 at R6). γ_novel=0.309, γ_ids=0.097, C(H,E)=0.889.
  174 unique IDs (104 after prefix stripping). 26.6% churn (vs Run 9: 84.5%).
  Logs: `bench/logs/baseline_confer_run10_20260403/`.
- **Run 10 FIXES APPLIED (3 April 2026, 12:18 BST):** 6 bugs fixed,
  1 diagnosed. B-Cell f-string escape (dead since creation — NameError
  in `_verify_z3` crashed entire cell, hidden by silent `except: pass`).
  `continue` bypass restructured. `tau_sim` 0.8→0.33 in 3 locations.
  `no_exclusion_mode` prevents FSM terminal cascade. Finding-ID convergence
  added (3 consecutive zero-novel rounds). Silent `pass` → `logging.warning`.
  SymPy verified top 4 Run 9 claims: all already fixed or trivial. 465 tests
  pass. Run 11 provisional plan written (4 branches contingent on Run 10).
- **Run 9 COMPLETE (3 April 2026):** 20 rounds, 425 findings, 120 min.
  γ_raw=+0.157, C(H,E)=0.828. Terminated MAX_ROUNDS. 65 unique finding
  IDs (vs Run 8: 30). Churn 84.5% (vs 91.2%). All 5 models produced
  implementation-level findings (task packet fix worked). Immune pipeline
  active: 21 DUPLICATE verdicts, 404 UNCERTAIN. Gemini benched at R5.
  SIX INFRASTRUCTURE BUGS FOUND: (1) `continue` bypass — convergence check
  skipped for R5-R19; (2) hardcoded `tau_sim=0.8` — NK dedup unreachable;
  (3) FSM terminal cascade from ABORT; (4) B-Cell f-string escape — cell
  dead since creation; (5) silent `except: pass` hid bug 4; (6) no
  finding-ID convergence signal. 22 unique claims after cross-model dedup;
  14 valid new, 4 refuted, 4 need investigation.
  Logs: `bench/logs/baseline_confer_run9_20260403/`.
- **Run 8 COMPLETE (3 April 2026):** 20 rounds, 339 findings, 52 min.
  γ = −0.041 (not converging), C(H,E) = 0.789 (strong corroboration).
  91.2% churn rate (30 unique / 339 total). Task exhausted by Round 1.
  Logs: `bench/logs/baseline_confer_run8_20260402/`.
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
  found edge cases (format divergence, CoT budget). Exp17 immune+LB live
  validation. Exp18=FFF convergence (methodology test). Each iteration finds
  less fundamental problems. The methodology is converging on itself. Experiment
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
- **Experiment 18 COMPLETE (31 March 2026, `d85eb5a`):** First formal FFF
  methodology test. Three-way round-robin (Gemini → CX GPT-5.4 → Gemini) under
  CDSFL with find-fix-follow instructions. 7 genuine fixes from 3 rounds.
  Key finding: FFF produces integration-level issues standard confer misses.
  CX model/effort configuration critical (o4-mini: 0 genuine; GPT-5.4 xhigh: 5
  genuine). Convergence in 3 rounds. Logs: `bench/logs/gemini_fff_exp17_fixes/`.
- **Baseline confer runner BUILT + AUDIT FIXES (1 April 2026, `2b30423`+uncommitted):**
  `bench/run_baseline_confer.py` — standard CDSFL confer with CC2 + CX + Gemini
  on immune task area. FFF via situation directive. Sequential dispatch. 10
  structural fixes from code audit (process_round once-per-round, ModelResponse
  construction, CircuitBreakerTripped handler, task extraction 269K→114K chars).
  Three test runs diagnosed and fixed different bugs. Run 3 reached R3 with 58
  findings before session loss. Runner now structurally correct; needs clean re-run.
  Logs: `bench/logs/baseline_confer_20260331/`.
- **Baseline confer Run 5 LIVE (1 April 2026, `1247cc8`):**
  All 5 frontier models (CC2 + CX + Gemini + DeepSeek + ChatGPT) under CDSFL +
  FFF, xhigh reasoning, reviewing `dynamic_management.py` immune layer.
  Run 5 upgrades over Run 4: (1) **10 SymPy-confirmed fixes** to
  `dynamic_management.py` (z-threshold, false_positive_rate windowing, correlated
  failure, effective_window decay, FORMAT recovery, early-stop set comparison,
  diagnoses ordering, sensitivity decay, findings decline resolution).
  (2) **Multi-turn decomposed dispatch** as automatic fallback on single-turn
  failure — prompts split into WAIT-step chunks, FFF in final turn. Infrastructure
  in `decomposed_dispatch.py` (all 4 backends: Gemini, OpenRouter, DeepSeek, Codex).
  (3) **No-exclusion policy** — EXCLUDE/ABORT signals intercepted, overridden with
  multi-turn decomposed dispatch. No model ever dropped.
  (4) **FSM terminal state guard** — catches RuntimeError on terminal FSM, continues
  collecting data (Run 4 root cause fixed).
  (5) **γ-unified convergence** + **C(H,E) Popper corroboration** reporting.
  (6) **Checkpoint/resume** logic for crash recovery.
  Pre-seeded Codex + DeepSeek for decomposition (Run 4 CX timeout fixed).
  Run 4 logs preserved: `bench/logs/baseline_confer_run4_20260401/`.
  Run 5 logs: `bench/logs/baseline_confer_run5_20260401/`.
- **Baseline confer Run 5 COMPLETE (1 April 2026, `589c053`):**
  155 corrected findings from 5 models × 5 rounds. 31 unique bug clusters,
  16 critical (sev ≥ 0.85), 58% independently confirmed by 2+ models. Three
  systemic failure modes: state leaks (8 clusters), direction inversions (4),
  missing interface contracts (6). Duane γ=0.112 (NOT converged — rich
  unexplored surface). Popper C(H,E)=0.847 (strong). Infrastructure validated:
  multi-turn fallback (2/2 recoveries), no-exclusion (load-bearing — immune
  layer tried to kill all 5 models at R2), FSM terminal guard (load-bearing —
  caught terminal state R3-R4). ChatGPT parser bug discovered: 29 findings lost
  to JSON format mismatch (fixed). Analysis: `docs/experimental_notes/Run5_Analysis_2026-04-01.md`.
  Findings: `docs/experimental_notes/Run5_Findings_2026-04-01.md`.
  Logs: `bench/logs/baseline_confer_run5_20260401/`.
- **All 31 Run 5 bug fixes applied + FFF verified (1 April 2026, `589c053`):**
  All 31 immune layer bugs fixed in `dynamic_management.py`. FFF verification
  pass caught 4 additional issues: FH-1 regression (idempotent _record_failure),
  FH-2 hasattr smell (proper __init__), RV-4 missing pathology_counts clear on
  exhaustion, DC-1/DC-2 encapsulation (register_diagnoses() method). JSON parser
  fixed — JSON array detection as first-pass before tuple/marker parsers.
  Observation-only γ_input/γ_output/amplification wired into runner. 387 tests.
- **Run 6 COMPLETE (2 April 2026, wall-clock cap at 29,223s / 8h7m):**
  11 rounds, 299 findings, 5 models. Per model: ChatGPT 89, CC2 85,
  DeepSeek 49, Codex 43, Gemini 33. γ=0.027 (NOT converged), C(H,E)=0.863
  (strong corroboration). Terminated by wall-clock cap, not convergence.
  Mid-session fixes: chunking (`44adcad`), Codex per-chunk dispatch (`380368a`),
  parser false-positive (`bc09e78`), CC2→claude CLI (`de3e1ae`), parallel
  blind dispatch (`1647acb`).
  CHURN ANALYSIS: 44% of findings re-targeted previously-examined code.
  Severity inflated R0→R10 (avg 0.55→0.80). R0-R3 genuinely novel; R4-R10
  largely elaborate restatements. MATH: 64 findings, 8 SymPy-verified, 7 valid,
  4 genuinely valuable bugs. SOFTWARE: 6 code-verified, 5 true, 5 worth fixing.
  CRITICAL: γ alone is wrong stop criterion. Compound objective (A × γ_output)
  already detected churn passively. Proposed as primary churn guard.
  Amplification: ChatGPT A=1.67, DeepSeek A=1.56, Codex A=1.55, CC2 A=1.48,
  Gemini A=1.12. Logs: `bench/logs/baseline_confer_run6_20260401/`.
- **Run 7b COMPLETE (2 April 2026, `556e0af`):**
  20 rounds, 197 findings, 3,106s wall-clock. γ=0.393 (converging), C(H,E)=0.6624
  (moderate corroboration). Per model: Codex 116, DeepSeek 41, CC2 20, ChatGPT 11,
  Gemini 9. Ω churn guard active: 4 of 5 models benched (CC2, ChatGPT, DeepSeek,
  Gemini) when Ω < 0.10 for 2 consecutive rounds. Codex sustained through all 20
  rounds. Layer 3 (AdaptiveQuestionOptimiser) passive — referential_density showed
  strongest correlation with Ω (r=0.141).
  FOUR MAJOR CHANGES from Run 6:
  (1) **Compound objective Ω churn guard** — A × γ_output = (β_out/β_in) × (1 − β_out),
  peaks at β_out=0.5. Per-model benching when Ω < τ (0.10) for 2 consecutive rounds.
  Resolution parameter S (default 0.5) tuneable severity threshold.
  (2) **Per-model context budget** — 80K default, 30K DeepSeek override. "IT Crowd fix":
  when accumulated findings exceed budget, model gets fresh instance with summary-only
  context (finding IDs + one-line descriptions). Cross-model findings only (models
  never see their own prior findings).
  (3) **File split** — 6,890-line `dynamic_management.py` split into 12 modules in
  `bench/dm/` (strict two-level DAG, zero circular deps). Backward-compatible
  re-export shim preserves all imports. Each module under 25K tokens for single-pass
  model review. 427 tests pass unchanged through the shim.
  (4) **Decomposition coherence** — Three-tier extraction (TARGET full, INTERFACE
  sig+15 lines, SKELETAL def+docstring) with `_INTERFACE_CRITICAL_MARKERS` ensuring
  cross-component APIs visible in all sub-area rotations. Critical regex bug fixed
  (class methods were invisible to boundary detection due to matching against stripped
  lines). `_REMEDIATION_CHAINS` dict explicitly captured.
  Run 7 (predecessor) failed: DeepSeek hung due to unbounded context injection
  (~230K chars of prior findings on top of 190K base prompt). DeepSeek spent 470s
  generating 85,706 chars of CoT reasoning with 0 chars of visible content. Hard
  wall-clock cap via threading added. Logs: `bench/logs/baseline_confer_run7b_20260402/`.
- **Run 7b sy+f analysis COMPLETE (2 April 2026):**
  197 raw findings → 16 unique verified bugs (6 medium, 10 low). 76% of findings
  were churn (same bug re-reported across rounds). 3 false positives including
  Codex hallucinating missing @dataclass decorator 8 times (7% of Codex output).
  2 mathematical claims refuted by SymPy. Top bugs: self_diagnose() bypasses
  immune_feedback_enabled (0.55), pathology_key namespace mismatch (0.40),
  _verify_remediation key mismatch for kappa/mu (0.35), false_positive_rate
  windowing bias, global damping scalar, chain_exhaustion_rate double-count.
  Analysis: `docs/experimental_notes/Run7b_SyF_Analysis_2026-04-02.md`.
- **Run 9 INFRASTRUCTURE BUILT (2 April 2026, `eeb7f40` + `ac0bf47`):**
  6-cell immune agent pipeline mapping biological cell types to parallel
  verification agents: Dendritic Cell (triage), Cytotoxic T-Cell (code FFF),
  B-Cell (SymPy + z3 + statsmodels), NK Cell (dedup + false-positive DB),
  Helper T-Cell (confidence-weighted synthesis), Regulatory T-Cell (autoimmune
  prevention). Pipeline: DC (~1s) → [CT + B + NK parallel] (~30-60s) →
  HT + RT (~1s). All 6 agents structurally constrained by code — no agent
  relies on natural language instruction. CT agent uses Level 3 enforcement:
  schema-forced structured evidence with file:line:code citations, mechanically
  verified against actual source by `_verify_ct_claim()`. Verdict derived from
  verification results, not agent opinion. New tools integrated: z3-solver 4.16,
  statsmodels 0.14.6, uncertainties 3.2.3 via Python 3.13 discovery. B-Cell
  class-switches (SymPy → z3) when primary tool returns uncertain. NK Cell seeded
  with Run 7b false-positive patterns. Wired into runner as observation-only
  for Run 8; two flags flip for Run 9 (`observation_only=False`, `ct_enabled=True`).
  465 tests pass. Design: `docs/experimental_notes/Immune_Agent_Architecture_2026-04-02.md`.
- **Run 7b BUILD SESSION COMPLETE (2 April 2026, `4b70824`):**
  14 of 16 verified bugs fixed (1 reverted by SymPy falsification of fix itself).
  Key fixes: namespace unification via `_CHAIN_TO_COUNTER` mapping,
  `immune_feedback_enabled` suppression gate on `self_diagnose()`, per-trigger
  damping (3 independent channels), FPR exact windowed counting via `round_idx`
  on all `DetectorDiagnosis`, bivariate normal correlation with Frechet upper
  bound clamping, full lifecycle for check 3 (mu_novelty_disagree), hysteresis-
  based VM resolution, P-pass gate on self-check 2, threshold boundary fix.
  New `bench/verification_utils.py` (~500 lines): 3-stage quality gate — dedup
  via `_finding_similarity`, SymPy subprocess verification, AST structural
  verification. PM stage stubbed (disabled). OBSERVATION-ONLY for Run 8.
  Layer 3 switched from `active=False` to `active=True` — will steer prompts
  for first time based on referential_density correlation with Ω.
  Runner: quality gate wired after each round, termination reason fix for
  MAX_ROUNDS fallthrough, dynamic round banner. 427 tests pass.
  SymPy+FFF verification of fixes caught 2 additional bugs in new code:
  quality gate self-dedup (current round in prior_findings), checkpoint
  serialisation of new fields. Both fixed.
- **PM Filter + Adaptive Immune Verification DESIGNED (2 April 2026):**
  Three-stage automated quality gate between rounds: (1) innate immunity —
  similarity dedup + SymPy + AST checking (zero cost, sub-second), (2) adaptive
  immunity — parallel verification agents via local `claude` CLI with full tool
  access (reads actual files, runs SymPy, AST-parses source; zero marginal cost
  on Max subscription), (3) regulatory T-cells — meta-verification agents that
  prevent over-rejection. All existing infrastructure (verify_sympy(), Finding.verified,
  _finding_similarity(), Role.PM) needs wiring, not building. Nested D-decay
  convergence at all three levels. 5 falsifiable questions registered.
  Design: `docs/experimental_notes/PM_Filter_Architecture_2026-04-02.md`,
  `docs/experimental_notes/Adaptive_Immune_Verification_2026-04-02.md`.
- **Input complexity module BUILT (1 April 2026, test article):**
  `bench/input_complexity.py` — Heaps β on input text (γ_input), output
  complexity (γ_output), amplification factor A = β_output/β_input, compound
  objective (A × steepness, optimal at β_out=0.5 — Occam emerges from maths).
  Wired into runner as observation-only measurement. Not used for dispatch.
  36 tests. Notes: `docs/experimental_notes/Input_Complexity_Decay_Curves_2026-04-01.md`,
  `docs/experimental_notes/Amplification_Factor_2026-04-01.md`.
- **Experiment 20 runner BUILT (30 March 2026, `e11b4a2`):**
  `bench/run_exp20_confer.py` — sequential confer architecture (Phase 1+2 of
  Whole Body Architecture). Fingerprint-based dispatch ordering (strongest model
  first, player_manager last as arbitrator). Attributed findings with
  `[source: model_id]`. Three output types: NOVEL, VALIDATION, CHALLENGE.
  Position-aware prompts (first reviewer, confer, arbitrator). Inherits
  decomposition and feasibility gate from Exp 17. Pending: preflight + canary
  test before launch. Launches after Exp 17 findings are collated and integrated.
  (Renumbered from Exp 18 to Exp 20 after FFF convergence work claimed Exp 18.)
- **Whole Body Architecture designed (30 March 2026):** Design note at
  `docs/experimental_notes/Whole_Body_Architecture_Plan_2026-03-30.md`.
  Three communication layers: nervous system (dispatch sequencing), circulatory
  system (attributed finding flow), endocrine system (adaptive pacing signals).
  Four phases — Exp 20 implements Phases 1 (attributed findings) and 2
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
  identified as missing piece. Exp 19 combines composable directives with FFF
  as a 2-condition test (standard vs FFF). Analysis:
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
  issue discovery. Now formally tested as Experiment 18 (FFF convergence).
  Exp 19 combines composable directives with FFF as a 2-condition test. Also
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
- **Gemini 9-page proposal P-passed (31 March 2026):** 2 genuinely useful
  (parallel blind dispatch, hybrid async-then-sync), 6 already implemented
  (churn), 1 mathematically incorrect (SI formula — SymPy falsified sign
  inversion on contradictions), 2 deferred (epistemic mesh/sovereign shards).
  Founder decision: reasoning_effort stays at xhigh (max capability, not
  throttled). User-configurable reasoning is a separate future feature.
- **Outstanding fixes tracking file (31 March 2026):** Persistent record of
  ALL unimplemented items from 17 TTS files and experimental notes, cross-
  referenced against codebase. Prevents context-loss from losing track of
  deferred work. File: `docs/experimental_notes/Outstanding_Fixes_And_Deferred_Items_2026-03-31.md`.
- **Founder decision — incremental testing (31 March 2026):** No multi-fix
  smoke tests. One variable at a time, measured against a known baseline.
  Sequence: (1) standard CDSFL baseline confer with CC2+CX+Gemini, (2) add
  CX MCP/plugin flags, (3) add parallel dispatch, (4) add WBA attribution.
  Each change measured independently.
- **Next:** Run 5 complete → apply findings → γ_input complexity routing →
  CX flags → parallel dispatch → WBA attribution → Exp 19 → Exp 20 → Bench Run 2.
  Founder observations: `docs/experimental_notes/Founders_FFF_Observations_2026-03-31.md`.
  Outstanding items: `docs/experimental_notes/Outstanding_Fixes_And_Deferred_Items_2026-03-31.md`.
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
    run_baseline_confer.py    -- Baseline confer runner (Run 5-7b)
    run_exp17_immune.py       -- Exp 17: immune + LB live validation runner
    run_exp20_confer.py       -- Exp 20: sequential confer runner (Whole Body)
    dynamic_management.py     -- Re-export shim (75 lines, backward compat)
    dm/                       -- Dynamic management modules (split from 6,890-line monolith)
      _types.py               -- Config, enums, dataclasses (shared vocabulary)
      _role_assignment.py     -- RoleAssignment (Area 1)
      _load_balancer.py       -- Allocation, LoadBalancer (Area 2)
      _fsm.py                 -- RoundProgressionFSM (Area 3)
      _convergence.py         -- ConvergenceDetector, similarity (Area 4)
      _diminishing_returns.py -- DiminishingReturnsDetector (Area 5)
      _immune.py              -- DetectorHealthMonitor (immune layer)
      _failure_handler.py     -- FailureHandler, CorrelatedFailureModel
      _events.py              -- ManagerEventStream
      _manager.py             -- DynamicManager (orchestrator)
      _validation.py          -- validate_all_reductions
    input_complexity.py       -- γ_input, γ_output, A, Ω, Layer 3 optimiser
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
