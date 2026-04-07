# Recovery Protocol

Last updated: 7 April 2026 07:10 BST

How to rebuild full working context from the repository alone after a
session loss, compaction event, or fresh start with a new model instance.

## Minimum Recovery (2 minutes)

1. Read `resources/ONBOARDING.md` — current project state, architecture,
   key concepts
2. Run `git log --oneline -10` — what changed recently
3. Run `git status` — any uncommitted work
4. Check if bench test is running: `ps aux | grep run_round_robin`
5. If resuming Experiment 12 fixes: read `bench/logs/experiment_12/experiment_12_report.json`
6. If resuming meta-test fix work: read `~/.claude/plans/agile-wondering-hejlsberg.md`
7. For Exp12 analysis: read `~/Desktop/Accessibility/Exp12_Final_Analysis_2026-03-29.txt`
8. For UX vision context: read `~/Desktop/Accessibility/CDSFL_UX_Vision_Sketch_2026-03-28.txt`

This is enough to resume most tasks.

## Current Pending Work (7 April 2026, 05:48 BST)

Experiments 12–36 ALL COMPLETE. 690 tests pass.

EXP 35 COMPLETE (6 April 2026, ~18:00 BST):
  PolicyEngine review, relay mode, 5 models, 23 rounds.
  533 raw findings, 79 canonical, 9 CONFIRMED (11.4%), 0 MERGED.
  γ=0.650 (strong depletion). Gate never triggered: open_ch=31 permanent blocker.
  Extension stall detector terminated experiment.
  Post-run: 6 immune pipeline fixes applied. 7 PolicyEngine fixes applied.
  Console: bench/logs/exp35_console.log
  Logs: bench/logs/exp35_pe_20260406T152126Z/

EXP 35 POST-RUN VERIFICATION (6 April 2026, 20:30-22:00 BST):
  79 canonical findings → 18 verified unique issues (4.4:1 dedup ratio).
  2 claims REFUTED (C0029 int exclusion, C0039 default-not-in-allowed).
  17 empty/malformed parser artifacts, 2 verdict-only entries excluded.
  Programmatic: AST analysis, text search, schema cross-reference.
  TTS: ~/Desktop/CDSFL_tts/Exp35_Verification_Analysis_2026-04-06.txt
  Analysis: experimental_notes/Exp35_Verification_Analysis_2026-04-06.md

IMPLEMENTED THIS SESSION (all committed and tested, 690 pass):
  1. Immune pipeline fixes (6 fixes to immune_agents.py, insect_brain.py)
  2. PolicyEngine fixes (7 fixes to engine.py, schema.toml, physics.toml)
     - load_schema(): default type + allowed_values validation
     - _compute_provenance() Layer 4: missing model_config merge
     - validate(): bidirectional HARD coverage, type scanning, min_layer, unknowns
     - diff_policies(): task_id_a/task_id_b params
     - Schema fixes: advisory_d_after_round min_layer, physical_bounds_check namespace,
       pipe_mode + json_schema_in_prompt added
  3. Convergence gate softening (both runners):
     - open_ch == 0 → stability-based: not increasing for OPEN_CH_STABILITY_WINDOW (3) rounds
     - open_ch_history tracking with checkpoint save/restore
  4. CC2v verification agent (both runners):
     - _VERIFICATION_PROMPT_TEMPLATE: structured FFF prompt for CC2
     - _verification_step(): batch OPEN findings, dispatch to CC2, parse verdicts
     - Confidence-gated (0.7): CONFIRM/REJECT/DUPLICATE/ESCALATE
     - Wired into main loop after immune bridge, stats logged in round_data
     - Activates from round 6, batch size 6
  5. Stall-convergence detector (both runners):
     - _check_stall_convergence(): complementary secondary convergence signal
     - Checks open_ch + contested static for STALL_WINDOW (3) rounds + gamma
     - Two tiers: advisory (γ ≥ 0.30, log only) and terminate (γ ≥ 0.45, STALL_CONVERGED)
     - Independent from primary gate — both run every round, both logged in round_data
     - Four termination states: STATE_CONVERGED, STALL_CONVERGED, EXTENSION_STALLED, BUDGET_EXHAUSTED
     - stall_history tracked with checkpoint save/restore
  6. CX + Gemini Runner 36 pre-flight review (7 April 2026, 00:05 BST):
     - 12 findings, 9 TRUE, 3 PARTIAL, 0 FALSE — 100% genuine rate
     - 5 must-fix items applied to BOTH runners:
       (a) Checkpoint ordering: moved write after convergence/stall checks
       (b) ESCALATE bypass: exempted from confidence gating (was dead code)
       (c) ESCALATE re-selection: cc2v_escalated flag, excluded from batch
       (d) mark_verified removal: CC2v CONFIRM → resolve() only
       (e) REFUTED in build_summary: added to resolved section
     - Review: experimental_notes/CX_Gemini_Runner36_Review_2026-04-07.md
     - TTS: ~/Desktop/CDSFL_tts/CX_Gemini_Runner36_Review_2026-04-07.txt
  7. ANALYSE step added to FFF (7 April 2026, 01:09 BST):
     - FFF → FIND-FOLLOW-ANALYSE-FIX in _PRESET_FFF and _PRESET_META_STRUCTURED
     - ANALYSE: dispassionate assessment gate (CONFIRMED/UNCERTAIN/REJECTED)
     - Prevents premature fixes on uncertain findings
  8. change_focus ITC adaptation (7 April 2026, 01:09 BST):
     - _build_change_focus_instruction(): registry-aware focus redirect
     - Wired into star and relay prompt builders in both runners
     - Fires on DEGRADATION: tells model to issue verdicts/merges, not re-describe
     - Registry passed as Optional param to dispatch functions

EXP 34 ANALYSIS COMPLETE (6 April 2026):
  81 canonical → 33 verified unique. 17 fixes applied to endocrine.py.
  Analysis: experimental_notes/Exp34_Analysis_and_Exp36_Plan_2026-04-06.md

CX + GEMINI RUNNER REVIEW COMPLETE (6 April 2026, 16:15 BST):
  11 findings claimed, 1 confirmed (alias map scoping). Fixed in both runners.
  Review: experimental_notes/CX_Gemini_Runner_Review_2026-04-06.md

EXP 36 COMPLETE (7 April 2026, 05:34 BST):
  Evidence layer review (evidence.py, ~420 lines), star topology, 5 models.
  23 rounds (20 base + 3 extension), 224 min. EXTENSION_STALLED.
  452 raw → 153 canonical (33.8% novelty rate). γ=0.411.
  CC2v: 50 verdicts (25C/6R/11M/8E), 9 HIL escalations.
  Burst reasoning at R8: 21 novel (72% rate) from all-model restart_fresh.
  Key design findings:
    (a) ITC-convergence feedback loop — restart_fresh sustains novelty, blocks gate
    (b) Contested → HIL escalation needed (1-2 contested blocked gate R12–R23)
    (c) Discovery efficiency (novel/raw) as complementary convergence signal
    (d) Meta-cognitive decay feedback — inject novelty trajectory into model prompts
    (e) B Cell v2 Z3 counterexample working, v2 activation indicated for Exp 37
  Console: bench/logs/exp36_console.log
  Logs: bench/logs/exp36_evidence_20260407T004931Z/
  Results: experimental_notes/Exp36_Results_2026-04-07.md
  Session findings: experimental_notes/Exp36_Session_Findings_2026-04-07.md
  TTS: ~/Desktop/CDSFL_tts/Exp36_Results_2026-04-07.txt
        ~/Desktop/CDSFL_tts/Exp36_Session_Findings_2026-04-07.txt
        ~/Desktop/CDSFL_tts/Exp36_Burst_Reasoning_Analysis_2026-04-07.txt
        ~/Desktop/CDSFL_tts/Exp36_Live_Analysis_CDSFL_as_Bench_2026-04-07.txt

EXP 36 POST-RUN VERIFICATION (7 April 2026, 07:06 BST):
  Three-workstream independent verification (FFAF protocol):
  Mathematical (NumPy/SciPy): 4 CONFIRMED, 3 UNCERTAIN, 0 REJECTED.
    - Phase 1 exponential decay R²=0.985, R8 burst z=3.63, gamma correct ±0.0005
    - ρ decline p=0.17 (directionally correct, underpowered)
  AST: 7 code bugs CONFIRMED, 1 REJECTED (nonlocal _intersect = valid Python).
    - 5 major families: payload guard, export_bundle, _classify_event, verify_bundle, regex
    - 2 additional: trace_finding ordering, EvidenceBundle asymmetric API
  Deep analysis: 8 CONFIRMED, 2 UNCERTAIN, 0 REJECTED.
    - DeepSeek late-stage churn dominance (55.6% of extension output)
    - Gemini output spikes anticorrelate with novelty
    - ITC conflates degradation with depletion (100% DEGRADATION across all models)
    - 3/5 convergence gate conditions non-contributing post-R6
    - Parser artifacts consuming 18% of CC2v slots
    - CC2v confirmations dominated by one bug family (12+ re-confirmations)
    - Context growth unbounded: 406% of budget by R22
  KEY RESULT: 153 canonical = ~9 unique bugs, 17:1 dedup ratio (worst in project).
  Bugs are real. Volume is churn. Three churn drivers: ITC feedback loop, dedup
  failure, context inflation.
  Verification: experimental_notes/Exp36_Verification_Analysis_2026-04-07.md
  TTS: ~/Desktop/CDSFL_tts/Exp36_Verification_Analysis_2026-04-07.txt

NEXT STEPS:
  1. Manual dedup COMPLETE (programmatic: 153 → ~9 unique, see verification analysis)
  2. Implement 13 design improvements for Exp 37:
     Original 7 (from Session Findings):
     - Contested → HIL escalation (5-round threshold)
     - Discovery efficiency metric (ρ = novel/raw)
     - Consolidation phase (ITC change_focus only in final 3 rounds)
     - Decay-rate convergence criterion
     - Meta-cognitive decay feedback in star topology prompt
     - v2 shadow activation (Helper T v2, B Cell v2)
     - Classifier/timeout fixes
     Deep analysis additions (6):
     - Per-model ρ tracking with targeted ITC intervention (HIGH)
     - Gamma-aware ITC DEGRADATION threshold (HIGH)
     - Dynamic stall detector terminate threshold
     - Pre-filter findings before CC2v queue (HIGH)
     - Dedup-aware CC2v (check prior confirmations) (HIGH)
     - Context windowing for long runs (HIGH)
  3. CC2 Option A remaining 3 agents (structural/semantic/integration) — design only

ARCHITECTURAL GAPS (remaining):
  - Immune shadow functions still named *_shadow() despite being PRIMARY/ACTIVE
  - CC2 Option A structural/semantic/integration agents (3 of 4) — design not coded
  - Python 3.9 → 3.12+ upgrade (Gemini SDK warnings)

EXP 32 COMPLETE (5 April 2026, 10:26 BST):
  Meta-experiment: 5 models analysed convergence data from Exp 30/31.
  10 rounds, 200 findings, 29 min. BUDGET_EXHAUSTED(10).
  Unanimous: convergence occurred in Exp 31 but 5 instrumentation failures
  prevented detection. 4/5 consensus on design parameters.
  PARTIAL CONFOUND: anchoring framing biased models toward optimising for
  convergence over scientific rigour. Models recommended fewer models (3),
  fewer rounds (8-10), and demoting gamma — all self-serving.
  Logs: bench/logs/exp32_meta_20260405T085629Z/
  Results: experimental_notes/Exp32_Results_2026-04-05.md

  FOUNDER OVERRIDES (correcting model self-optimisation):
  - Model count: 3+1 → 5 (diversity is a research variable)
  - Round budget: 8-10 → 21 (mathematical model predicted 20)
  - Gamma: telemetry-only → scale-dependent (telemetry R1-14,
    soft gate R15-19, hard gate R20+)
  - Earliest stop: R6 → R12

  ADDITIONAL FIXES APPLIED (post Exp 32):
  - E31-14: Truncation marker attribution (cosmetic, last unfixed finding)
  - LLM classifier shadow: OpenRouter calls disabled (use CLI Haiku)
  572 tests pass.

EXP 33 RUNNER BUILT (bench/run_exp33_endocrine.py):
  First code review using star/blackboard topology. Target: endocrine.py.
  21 rounds (extension to 24). 5 models. Neutral framing (no hypothesis).
  FindingRegistry class implements canonical blackboard. FFF is prompt-only
  (no enforcement, no rejection). State-based convergence gate with
  programmatic status transitions (CONFIRMED at 2+ independent models,
  MERGED on merge verdict, CONTESTED on late challenge) + scale-dependent gamma.

EXP 34/35/36 RUNNERS BUILT (5 April 2026):
  Three separate experiments, one per test article:
  - Exp 34 (bench/run_exp34_endocrine.py): endocrine.py review
  - Exp 35 (bench/run_exp35_policy_engine.py): PolicyEngine (engine.py + schema.toml)
  - Exp 36 (bench/run_exp36_evidence.py): Evidence layer (evidence.py)
  All runners share the corrected FindingRegistry with programmatic status
  transitions, UNCONFIRMED (not REJECTED) status, and no FFF enforcement.
  Star/blackboard topology. 21-round budget (extension to 24).

RUNNER FITNESS CONFER (5 April 2026, ~21:08 BST):
  CX (GPT-5.4, reasoning high) + Gemini 3.1 Pro reviewed all 3 runners under
  full CDSFL. One round, individual convergence called by CC.
  Logs: bench/logs/confer_runner_review/

  11 CONFIRMED BUGS FIXED (all 3 runners + runner_core.py):
  P0 — Blocking:
  1. MERGE semantics backwards — canonical target marked MERGED, not duplicate.
     Fix: _resolve_merge_source() records MERGE on source entry.
  2. Convergence gate — only novelty checked across 2-round window.
     Fix: _evaluate_gate_conditions() + gate_history tracks all 5 conditions.
  3. contested_count ignores non-OPEN — late challenges invisible after CONFIRMED.
     Fix: check all non-MERGED, compare challenge timing vs latest confirm.
  P1 — High:
  4. Resume doesn't restore registry — fresh FindingRegistry on resume.
     Fix: runner_state.json persists registry + convergence state per round.
  5. Gamma estimation wrong — first/last cumulative only, raw findings.
     Fix: log-log regression over canonical novelty_counts.
  6. Verdict parser em-dash — prompt uses U+2014, regex only matched ASCII.
     Fix: regex accepts Unicode dashes + leading whitespace/list markers.
  7. Multi-turn fallback split — splits on "=== FILE:" but headers differ.
     Fix: regex split on actual TARGET/SCHEMA/CONTEXT headers.
  8. UNSTRUCTURED fallback creates fake findings on verdict-only responses.
     Fix: suppress fallback when verdict patterns detected (runner_core.py).
  P2 — Medium:
  9. Missing UNCONFIRMED sweep — OPEN findings never finalised.
     Fix: resolve remaining OPEN to UNCONFIRMED before signal_complete().
  10. SUPERSEDES in prompt but not parsed — removed from all prompts.
  11. Popper C(H,E) invalid math (exp36 only) — removed entirely.

  1 FALSE POSITIVE REJECTED:
  - Alias collision (Gemini, all 3 reviews) — runner_core.py already prefixes
    finding IDs with model_id_. Gemini missed the shared parser.

CDSFL TOPOLOGY SPEC CREATED (5 April 2026, ~21:45 BST):
  New formal specification: bench/directives/universal/cdsfl_topology_formal.md
  8 sections (T1-T8) formalising the multi-model star/blackboard protocol:
    T1. Star/blackboard topology definition
    T2. Finding status model (OPEN/CONFIRMED/CONTESTED/MERGED/UNCONFIRMED FSM)
    T3. Merge contract (explicit directionality, anti-loop invariant)
    T4. Convergence gate (temporal conjunction over boolean gate history)
    T5. Gamma estimation (log-log regression, canonical novel input)
    T6. Round taxonomy (finding/verdict/mixed/empty response types)
    T7. Durability contract (state persistence invariant for resume)
    T8. P-pass boundary tracing (dependency-chain completeness)
  Core spec amendments:
    cdsfl_core_formal.md §3: boundary tracing added + cross-reference
    cdsfl_core.txt: boundary tracing paragraph added
  Runner implementations updated to match schema (CONTESTED state, merged_into).
  Provenance: derived from runner fitness confer findings.

  PENDING:
  - Implement CC2 Option A multi-agent (4-way split: structural/semantic/integration + verification)
  - Soften convergence gate open_ch condition (stability-based, not == 0)
  - Python 3.9 → 3.12+ upgrade (Gemini SDK warnings)

EXP 31 COMPLETE (5 April 2026, 07:38 BST):
  Post-fix validation. 15 rounds, 360 findings, BUDGET_EXHAUSTED(15).
  κ=0.619, γ=0.106. All 5 models active. γ rising (0.000→0.106) — opposite
  to Exp 30 (0.567→0.320, diverging). 39 prior fixes reduced re-discovery.
  Mid-experiment: convergence ordering fix, signal_complete precedence,
  B-Cell UNCERTAIN→HIL (Stage 5.5), Good Enough + merge instructions,
  Merkle sealing. 18 findings catalogued (E31-01 to E31-18).
  Critical blocker: deep-copy propagation (E31-01) makes bug-closed gate
  dead code. κ=0.619 proves models agree; γ=0.106 proves they can't close.
  Merkle sealed: 108 records, chain verified.
  Logs: bench/logs/exp31_postfix_20260405T041753Z/
  Findings: experimental_notes/Exp31_Interim_Findings_2026-04-05.md
  TTS: ~/Desktop/CDSFL_tts/Exp31_Final_Findings_2026-04-05.txt

EXP 30 POST-ANALYSIS (5 April 2026, 04:47 BST):
  Deep analysis of non-convergence: fix-level churn was the root cause.
  232 proposed fixes for ~83 distinct bugs. Models debating alternative
  solutions instead of finding new bugs. κ_rate oscillated due to sustained
  novelty from directed messaging.

  ARCHITECTURAL FIXES APPLIED:
  1. Bug-closed gate in NK cell v1+v2 — first programmatically verified fix
     wins. finding.verified = True after pyright/ruff/bandit/pytest pass in
     sandbox. Subsequent findings about same bug rejected by NK cell.
  2. Programmatic fix evaluation (Stage 4 in immune pipeline) — evaluate_fix()
     from endocrine.py wired into run_immune_pipeline(). No model opinion.
  3. BUDGET_EXHAUSTED status — max_rounds sets converged=False, reason=
     "BUDGET_EXHAUSTED". Honest termination, not false convergence.
  4. Context formatting — CLOSED/PENDING/OPEN bug status shown to models.
     Models told "do not relitigate CLOSED bugs."

  BUG FIXES FROM EXP 30 FINDINGS (39 total):
  immune_agents.py (18): log-odds sign, Z3 verification, SMT-LIB negation,
     CLI thread lock, reconciliation margin, skin barrier (3), NK v1 flow,
     sympy regex, dendritic AND join, barrier rejection, autoimmune override,
     dead code, lazy discovery, AST cache, statistical claims, tool_usage.
  insect_brain.py (10): checkpoint recovery amnesia, immune serialisation,
     gamma_hat div-by-zero, failure checkpoint, atomic write, exception
     specificity, max_rounds=0, truncation marker, docstring, newline fix.
  verification_chain.py (8): epoch ordering, orphan epochs, CLI/API contract,
     seal_epoch idempotency+fsync, deep copy, load_json validation,
     sub-second timestamps, error truncation.

  Tests: 571 passed, 0 failed.

PENDING (as of Exp 30 post-analysis — now superseded, see Current Pending Work above):
  All items below COMPLETE. Exp 32 done, E31 fixes applied (572→688 tests),
  Exp 33/34/35/36 runners built, topology spec created.

HIL COMPARISON EXPERIMENTS COMPLETE (4 April 2026, 04:45 BST):
C1 (Realistic HIL): 25 findings, 9/9 verified, 0 FP. 5 rounds, ~3 min.
C4 (CDSFL+Meta structured): 16 survivors (12 retracted), 16/16 verified, 0 FP. 16 rounds, ~13 min.
Combined: ~33 unique verified findings (+32% coverage vs best single condition).
Key: C1 finds cross-component bugs (18 unique). C4 finds formal/injection bugs (14 unique).
Overlap: only ~5 findings. Complementarity thesis VALIDATED.

THREE-LAYER SCHEMA DISCOVERY (4 April 2026, 04:45 BST):
Critical reframing of CDSFL methodology:
  Layer 1: Meta structured prompting — reasoning format (premises, trace, conclude)
  Layer 2: CDSFL constraints — rules of engagement (FFF, falsification, constraint classification)
  Layer 3: Session architecture — full conversational mode as DEFAULT, ITC as FALLBACK ONLY
ITC (IT Crowd principle / cell decomposition) is NOT the default operating mode.
It activates when: model fails, context degrades, single-pass problems, or diminishing returns.
Normal mode = full continued conversation under CDSFL constraints.
C5 experiment proposed: full conversational + CDSFL constraints + Meta prompting. Predict 30+ findings.
TTS: ~/Desktop/CDSFL_tts/Three_Layer_Schema_Discovery_2026-04-04.txt
Analysis: experimental_notes/HIL_Comparison_Analysis_2026-04-04.md
Logs: bench/logs/hil_comparison_c1_20260404/, bench/logs/hil_comparison_c4_20260404/

C5 THREE-LAYER SCHEMA VALIDATION (4 April 2026, 06:16 BST):
Automated script ran 8-round continued conversation with Gemini 3.1 Pro.
CDSFL + Meta structured prompting as system instruction (not user prompt).
Same code artifact (927bfbc), same model as C1/C3/C4.
Results: 27 consolidated findings (36/40 registry confirmed + 6 novel).
3 self-retractions. 0 FP. 5 cross-component. 5 novel constructs.
100% findings include fixes. 90% prior confirmation. 11.6 min. No ITC trigger.
Automated verdict: PARTIAL (consolidation depressed ID count below 30 threshold).
Qualitative: combines C1 breadth + C4 depth. Schema partially validated.
MF-28 retracted by C5 as false positive (trailing \d+ prevents empty match).
Novel findings: path traversal, empty string bypass, prompt injection,
Confident Hallucination Highway (DC misroute + B Cell injection + HT inversion).
Novel constructs: Epistemic Routing Layer, Reconciliation Gate, Formalisation
Agent, typed LLM classifier, lazy tool discovery.
Scripts: bench/c5_three_layer_schema.py, bench/c5_prompts.py, bench/c5_verify.py
Logs: bench/logs/c5_20260404T050417Z/
TTS: ~/Desktop/CDSFL_tts/C5_Three_Layer_Results_2026-04-04.txt

RUN 11 COMPLETE (4 April 2026, 01:54 BST) = Exp 28b:
2 rounds, 59 findings, 42 min. Fastest convergence in bench history.
γ_novel=0.737, C(H,E)=0.873. CC2 dispatch failure (21 min timeouts),
Gemini benched (Ω<0.1), 67% immune rejection in R1.
Shadow v2 first production data: NK v2 caught 9 intra-round dups,
B-Cell v2 ran 42 SMT-LIB checks. All v2 shadows fired correctly.
Analysis: experimental_notes/Run11_Rapid_Convergence_Analysis_2026-04-04.md
Logs: bench/logs/baseline_confer_run11_20260404/

CC2 DISPATCH DIAGNOSIS (4 April 2026, 02:10 BST):
Root cause: 300s Python subprocess timeout kills CC2 before completion.
Not a CLI limit — entirely in our code. Three-layer fix planned:
  Layer 1: increase timeout 300s→900s, retries 3→1 (immediate, free)
  Layer 2: cell-level decomposition for adaptive rounds (Exp 29)
  Layer 3: parallel split for blind rounds if retained (Exp 29)
Diagnosis: experimental_notes/CC2_Dispatch_Diagnosis_2026-04-04.md

EXP 29 STRATEGIC DIRECTION (4 April 2026, 02:57 BST):
First integration test of the TARGET ARCHITECTURE, not another calibration.
Full conversational mode — no blind round. Models confer as peers under
CDSFL/FFF with insect brain as mechanical relay. Five architectural layers:
  1. Persistence layer (built, operational)
  2. Immune layer (operational, v2 shadows validated, ready to activate)
  3. Adaptive layer / AQO (built, switchable)
  4. Insect brain / nervous system (designed, not built — CRITICAL PATH)
  5. Endocrine system / pacing signals (designed, not built — not blocking)

SEQUENCE TO BENCH RUN 2:
1. ✓ Integrate Run 11 findings — DONE
2. ✓ Fix 40 Master Finding Registry bugs — DONE (all P0-P3 tiers)
3. ✓ Implement C5 novel constructs — DONE (3/5 built, 2 deferred)
4. ✓ Activate v2 immune components — DONE (all active)
5. ✓ Build insect brain — DONE (bench/insect_brain.py)
6. ✓ CC2 dispatch fix — DONE (300s→900s, retries 3→1)
7. → Exp 29 — NEXT (full integration test, subject: persistence layer)
8.   BENCH RUN 2 — 27 frontier STEM problems, full integrated architecture
9.   Unified experiment numbering — QC sweep

INSECT BRAIN ARCHITECTURE (NOW BUILT):
- Reactive coordinator, not deliberative. Gathers/processes/tabulates/commits.
- Models drive conversation under full CDSFL as peers.
- Implementation: bench/insect_brain.py (500 lines, 7 core functions)
- Design notes: experimental_notes/Insect_Brain_Architecture_2026-04-03.md
- Global mind vision: experimental_notes/Global_Mind_Architecture_2026-04-03.md

RUN 10 COMPLETE (3 April 2026, 16:44 BST):
- 7 rounds, 237 findings, 37 min. FIRST NATURAL CONVERGENCE.
- DM kappa=1.0 at R6. γ_novel=0.309, γ_ids=0.097, C(H,E)=0.889.
- 174 unique IDs, 26.6% churn (vs Run 9: 84.5%, Run 8: 91.2%).
- Sequential file delivery replaced sub-area rotation for decomposed models.
- CC2 excluded from decomposition + wall-clock timeout 5×.
- FSM checkpoint-replay terminal fix (reset on DIMINISHED during replay).
- Logs: bench/logs/baseline_confer_run10_20260403/
- Analysis: experimental_notes/Run10_Results_2026-04-03.md

RUN 8 COMPLETE (3 April 2026, 00:39 BST):
- 20 rounds, 339 findings, 52 minutes. γ = −0.041, C(H,E) = 0.789
- Terminated: MAX_ROUNDS (no convergence detected)
- CRITICAL FINDING: 91.2% churn rate (30 unique finding IDs / 339 total)
- Task exhausted by Round 4 — all genuine issues found. Rounds 5-19 = restatement.
- Analysis: experimental_notes/Run8_Analysis_2026-04-03.md
- Logs: bench/logs/baseline_confer_run8_20260402/

RUN 9 INFRASTRUCTURE BUILT (2 April 2026, `eeb7f40` + `ac0bf47`):
- 6-cell immune agent pipeline (details in ONBOARDING.md)
- ALL 6 agents structurally constrained by code, not natural language
- CT agent Level 3 enforcement: schema + mechanical verification
- New tools: z3 4.16, statsmodels 0.14.6, uncertainties 3.2.3

RUN 9 COMPLETE (3 April 2026, 05:44 BST):
- 20 rounds, 425 findings, 120 min. γ_raw=+0.157, C(H,E)=0.828.
- 65 unique finding IDs (vs Run 8: 30). Churn 84.5% (vs 91.2%).
- All 5 models produced implementation-level findings (task packet fix worked).
- Immune: 21 DUPLICATE, 404 UNCERTAIN. B-Cell: 0 usage. CT: UNCERTAIN only.
- THREE INFRASTRUCTURE BUGS — all must be fixed before Run 10:
  1. `continue` bypass (line 1399): DM FSM terminal → exception handler
     skips γ-on-clusters convergence check. Ran for R2-R4 only. Fix: move
     convergence check outside try/except or into finally.
  2. Hardcoded `tau_sim=0.8` (line 1209): overrides calibrated 0.33. NK Cell
     dedup threshold unreachable. Fix: remove explicit kwarg, use default.
  3. DM FSM TERMINAL(FAILURE) at R5, never recovers. All immune dispatch
     recommendations flow through no-exclusion override only. Fix: investigate
     FSM state machine — why does EXCLUDE cascade into unrecoverable FAILURE?
- ADDITIONAL: B-Cell SymPy/z3 not firing (0 false_positive_db, 0 anomaly).
  CT returns UNCERTAIN on all but near-exact duplicates. Both need investigation.

RUN 10 FIXES APPLIED (3 April 2026, 11:45 BST):
All 7 action items resolved. 6 bugs fixed, 1 diagnosed:
1. DONE: continue bypass — convergence check restructured outside try/except
2. DONE: tau_sim 0.8→0.33 in runner, immune_agents.py, _types.py
3. DONE: FSM terminal — no_exclusion_mode prevents ABORT→FAIL_CRITICAL
4. DONE: B-Cell — f-string escape bugs in _verify_z3 (line 752) and
   _verify_statistical (lines 795-808). NameError crashed B-Cell silently
   via silent except:pass. B-Cell was DEAD for all runs since creation.
5. DONE: Silent pass → logging.warning in pipeline exception handler
6. DONE: Finding-ID convergence (3 consecutive zero-novel rounds)
7. DIAGNOSED: CT UNCERTAIN — claim_type mismatch + evidence verification.
   Partial improvement expected from B-Cell revival + better logging.
SymPy verified: top 4 restated findings (IM_F001-F005) all ALREADY FIXED.
465 tests pass. Commit pending.

RUN 10 PREP (mark for next run):
- Switch runtime from system Python 3.9 to Homebrew 3.13
  (/opt/homebrew/bin/python3.13). Eliminates: google-auth EOL warnings,
  `from __future__ import annotations` workarounds in decomposed_dispatch.py,
  tomli fallback shims in registry.py and composer.py, and puts us on a
  supported runtime. Do this between runs, not mid-run.

RUN 5 RESULTS (1 April 2026, COMPLETE):
- 155 corrected findings, 31 unique bug clusters, 16 critical (sev ≥ 0.85)
- 58% independently confirmed by 2+ models
- Duane γ=0.112 (NOT converged), Popper C(H,E)=0.847 (strong)
- Analysis: docs/experimental_notes/Run5_Analysis_2026-04-01.md
- Findings: docs/experimental_notes/Run5_Findings_2026-04-01.md
- Logs: bench/logs/baseline_confer_run5_20260401/

INPUT COMPLEXITY MODULE (1 April 2026, observation-only):
- bench/input_complexity.py — γ_input, γ_output, amplification A, compound objective
- Wired into runner as observation-only (not used for dispatch decisions)
- 36 tests passing
- Notes: docs/experimental_notes/Input_Complexity_Decay_Curves_2026-04-01.md
- Notes: docs/experimental_notes/Amplification_Factor_2026-04-01.md

EXPERIMENT 17 CODE FIXES COMPLETE + Exp 18 FFF CONVERGENCE COMPLETE (31 March 2026):
- Round 3 COMPLETE (140 findings). All applicable code fixes applied in 4 batches:
  8 IM + 9 LB + 14 VC + 4 MM = 35 fixes (commit `050fd20`). 351 tests passing.
- Three-way FFF round-robin (Gemini → CX GPT-5.4 → Gemini) converged in 3 rounds
  with 7 additional fixes (commit `d85eb5a`). Now formally Experiment 18.
- CX efficiency confer R2: 4 models × 2 rounds, 46 findings, converged.
- CLI efficiency fixes IMPLEMENTED in call_codex(): MCP servers disabled,
  plugins disabled, ephemeral mode. Reasoning effort reverted to xhigh
  (founder decision 2026-03-31: max capability, not throttled).
- Logs: `bench/logs/experiment_17/`, `bench/logs/gemini_fff_exp17_fixes/`
- Confer results: `bench/logs/cx_efficiency_confer_r2/`

EXPERIMENT 20 RUNNER BUILT (30 March 2026, `e11b4a2`):
- bench/run_exp20_confer.py — sequential confer (Whole Body Phase 1+2).
- Attributed findings, fingerprint dispatch ordering, NOVEL/VALIDATION/CHALLENGE.
- Pending: preflight + canary, then launch after Exp 17 collation.
- (Renumbered from Exp 18 to Exp 20 after FFF convergence work claimed Exp 18.)

WHOLE BODY ARCHITECTURE DESIGNED (30 March 2026):
- docs/experimental_notes/Whole_Body_Architecture_Plan_2026-03-30.md
- Nervous (dispatch sequencing), circulatory (attributed findings), endocrine
  (adaptive pacing). Exp 20 = Phases 1+2. Phases 3+4 = future.

CX PROMPT EFFICIENCY CONFER R1 COMPLETE (30 March 2026, `8c1dacb`):
- CX burns 155K tokens on 78 tool calls investigating codebase instead of
  producing findings. Fix: 6-field standard confer packet with embedded code,
  stdin piping, output-schema. 78% token reduction proven. ALL IMPLEMENTED.
- Record: `docs/experimental_notes/CX_Prompt_Efficiency_Confer_2026-03-30.md`

CX EFFICIENCY CONFER R2 COMPLETE (31 March 2026):
- CX hit usage limit after ~3h. 4-model confer under CDSFL diagnosed root causes.
- CLI audit: reasoning effort xhigh, 4 MCP servers loading, no ephemeral mode.
- Fixes implemented in call_codex(): -c model_reasoning_effort="medium",
  -c mcp_servers={}, -c plugins={}, --ephemeral. Confer: bench/logs/cx_efficiency_confer_r2/

MIDCA ANALYSIS COMPLETE (31 March 2026):
- CDSFL vs Cox et al. AAAI-16. 6/8 met, 2 partial, extends beyond MIDCA scope.
- Analysis: docs/experimental_notes/CDSFL_MIDCA_Analysis_2026-03-30.md

COMPOSABLE DIRECTIVE ARCHITECTURE P-PASSED + BUILT (31 March 2026):
- Four-layer stack: Universal → Domain → Phenotype → Situation.
- 5 falsification passes, 5 falsifiable questions. Dynamic composer BUILT.
- 5-model architecture confer: 3 rounds × 5 models (~191K chars). Open format.
- 5-model composer review confer: 2 rounds × 5 models (~303K chars). Problem box.
- All 6 problems solved. CX won all 6. ChatGPT strong second.
- Composer: bench/cdsfl_registry/composer.py (1,399 lines). All fixes applied.
- SymPy verified: 8 implementation claims + 12 mathematical model claims pass.
- Ising model needs bounded ψ: Σψ ≤ −Σlog(1−q_i).
- Two complementary coherence constructs: capacity-based (CC2/Gemini) + entropy-based (DeepSeek).
- Optimal directive window: product φ(L)·α(L) has unique maximum.
- Analysis: docs/experimental_notes/CDSFL_Composer_Review_Confer_2026-03-31.md
- Confer logs: bench/logs/composable_directives_confer/, bench/logs/composer_review_confer/

TTS OUTPUT PROTOCOL UPDATED (30 March 2026):
- New `tts-output-protocol` directive in CLAUDE.md replaces old tts-default-on
  + tts-repo-mirror. Per-project Desktop folders (e.g. `CDSFL_tts/`) + repo
  `experimental_notes/` as formatted .md. 141 files moved from Accessibility/.

6-ROUND MATHEMATICAL COHERENCE AUDIT CONVERGED (31 March 2026):
- Round 0: Gemini Phase 1 (8-chunk decomposed, 14,872 chars, 6 tasks)
- Round 1: SymPy 13/13 PASS + CC observations (5 items)
- Round 2: Gemini Phase 2 (namespace table, §9/§10 text, self-falsification)
- Round 4: 5-model review (CC2+CX+ChatGPT+DeepSeek+Gemini, 28,088 chars)
- Round 5: SymPy 10/10 PASS (ρ_eff domain, C(n) independence, Ising pairwise,
  normalised Ising, ⊥ probability, Λ uniqueness — all confirmed)
- Round 6: Gemini final resolutions + CX verification (3 APPROVE, 2 MODIFY)
- 8 items RESOLVED, 2 minor CX modifications outstanding (editorial)
- KEY OUTCOMES: normalised Ising with partition function Z, C(n) branching
  (independent vs correlated), namespace refactor (17 collisions), synthesis
  deferral operator τ_defer, A-N1 REJECTED, A-N3 null-vector guard
- Logs: bench/logs/gemini_math_audit/round{0-6}_*.{json,md}

FIND-FIX-FOLLOW PATTERN IDENTIFIED (31 March 2026):
- Founder's informal Gemini interaction pattern: find issue → fix it → explore
  consequences of fix. Three-step intra-model cycle produces scope expansion.
- Current CDSFL rounds require findings but not resolution within model's turn.
- Resolution-and-consequence obligation proposed for round instructions.
- Now formally tested as Experiment 18 (FFF convergence). Exp 19 = formal
  2-condition test (standard vs FFF).
- Also flagged: seeded sensitivity + NMI sycophancy trigger for evaluation.

ROUND 7 FFF AUDIT COMPLETE (31 March 2026, `e86d44e`):
- Gemini find-fix-follow on full appendix + Round 6 resolutions
- 6 integration issues found, all fixed, SymPy 10/10 PASS
- Model declared mathematically coherent and complete by Gemini
- First practical demonstration of find-fix-follow pattern

ROUND 8 GEMINI CONSTRUCT EVALUATION COMPLETE (31 March 2026):
- 9 constructs from informal founder-Gemini interaction evaluated under CDSFL FFF
- 3 ADOPT: seeded sensitivity (S_H), NMI diversity (δ_ij), sycophancy trigger
- 3 MODIFY: error re-injection (ν), HIL framing penalty, substrate ceiling
- 3 REJECT: Mayo severity (redundant), calibration ω (unnecessary), optimal stopping (covered)
- SymPy 6/6 PASS. Total audit: 8 rounds, 39 algebra checks, all passing
- Log: bench/logs/gemini_math_audit/round8_fff_eval_gemini_20260331T145404Z.json

MATHEMATICAL APPENDIX REWRITTEN (31 March 2026, `c7f9e7a`):
- All 8-round audit fixes applied. 826 → 1022 lines.
- §0.1 Ising, namespace refactor, τ_defer, null-vector guards, separability,
  ρ clipping, seeded sensitivity, NMI diversity, S_sync^emp, re-injection,
  HIL framing penalty, substrate ceiling. Post-edit SymPy 7/7 PASS.

EXP 17 CODE FIXES ALL APPLIED (31 March 2026, `050fd20`):
- 8 IM + 9 LB + 14 VC + 4 MM code fixes applied in 4 batches. 351 tests passing.
- Key fixes: pathology_key routing (IM_F013), remediation escalation reset (IM_F002),
  FFD allocation sort (LB_F001), verify_chain exception safety, atomic writes,
  kappa_rate clamping, estimate_gamma correction, remaining_value abs decay.

THREE-WAY FFF CONVERGENCE COMPLETE (31 March 2026, `d85eb5a`):
- Round 1 (Gemini): 2 findings — estimate_gamma inf, kappa_rate divergence masking.
- Round 2 (CX GPT-5.4 xhigh): 5 findings — verify_chain safety, Verifier robustness,
  mu+novelty routing, PM warning wiring, estimate_gamma zero-data refinement.
- Round 3 (Gemini): Convergence declared — no new findings above 0.5 severity.
- Three-way CC/Gemini/CX FFF round-robin under CDSFL. All fixes applied. 351 tests.
- Logs: bench/logs/gemini_fff_exp17_fixes/

GEMINI P-PASS COMPLETE (31 March 2026):
- Gemini's 9-page proposal P-passed. 2 genuinely useful (parallel dispatch,
  hybrid async-sync), 6 already implemented (churn), 1 mathematically incorrect
  (SI formula — SymPy falsified), 2 deferred (mesh/shards).
- Founder rejected reasoning_effort downgrade: max capability stays as default.
  User-configurable reasoning is a separate future feature.

OUTSTANDING FIXES TRACKING FILE WRITTEN (31 March 2026):
- `docs/experimental_notes/Outstanding_Fixes_And_Deferred_Items_2026-03-31.md`
- Persistent record of ALL unimplemented items from 17 TTS files and notes.
- Prevents context-loss from losing track of deferred work.

BASELINE CONFER RUNNER AUDIT FIXES APPLIED (1 April 2026):
- `bench/run_baseline_confer.py` — 10 structural fixes from code audit:
  process_round() called ONCE per round (not per-model), proper ModelResponse
  construction (content/response_time/round_idx), CircuitBreakerTripped handler,
  round_type parameter threaded through _dispatch_round, format_findings_for_context
  called with correct args, task extraction (269K→114K chars) before prompt building.
- Three attempted runs hit different bugs (task init, format_findings type error,
  ModelResponse field names). All fixed. Run 3 reached Round 3 with 58 findings
  before session context exhaustion killed it. Round 0 per-model JSONs saved;
  Rounds 1-3 lost (round_type NameError in save_output — now fixed).
- Runner is now structurally correct. Needs clean re-run.

NEXT STEPS (1 April 2026):
1. Re-run baseline CDSFL confer (all audit fixes now in code). Clean run expected.
2. After baseline: layer in CX MCP/plugin flags (one change, measured)
3. After that: parallel blind dispatch (one change, measured)
4. After that: WBA Phase 1 finding attribution (one change, measured)
5. γ unification (pre-Bench Run 2, pending founder confirmation)
6. Exp 19: FFF hypothesis test (runner built, ready)
7. Exp 20: sequential confer (runner built, ready)
8. Full bench run (Bench Run 2) — the finish line
Founder observations: `docs/experimental_notes/Founders_FFF_Observations_2026-03-31.md`
All outstanding items: `docs/experimental_notes/Outstanding_Fixes_And_Deferred_Items_2026-03-31.md`

STOPPING CRITERION (founder-defined): "Everything wired and fully operational
to an extent that we can turn it against the bench without wasted effort."

META-TRAJECTORY: Exp12=structural, Exp13=calibration, Exp14=design gaps,
Exp15=edge cases, Exp16=plan review, Exp17=immune+LB live, Exp18=FFF,
Exp20=confer. Founder decision: incremental changes only, one variable at a
time measured against baseline. No multi-fix smoke tests.

## Standard Recovery (5 minutes)

Everything above, plus:

5. Read `docs/FOUNDERS_NOTES.md` — design intent, chronological observations,
   known confounds, open questions
6. Read the latest bench test log: `tail -50 bench/logs/$(ls -t bench/logs/ | head -1)`
7. Check `docs/EXPERIMENTAL_RESULTS.md` for latest recorded results

## Full Recovery (10 minutes)

Everything above, plus:

8. Read `PAPER.md` — canonical technical statement (Parts I-XIV)
9. Read `docs/MATHEMATICAL_APPENDIX.md` — mathematical extensions including
   the cognitive measurement framework (§7) and emergence formalisations (§8)
10. Read `configs/README.md` — domain expert configuration system
11. Read `bench/cdsfl_registry/universal.toml` — current HARD constraints
12. Read `PRIVATE_NOTES.md` (if it exists locally) — known confounds and
    design decisions not yet public
13. Check Open Brain for session context:
    `python3 -m open_brain.cli session-context --agent cc`
14. Check IM service for inter-model communications:
    `python3 cw_handoff/im_service.py read`

## For the Founder Specifically

After compaction, the continuation summary is what I was thinking — not what
happened. It is never sufficient on its own. The external sources (git log,
bench logs, ONBOARDING.md) always take precedence over the continuation
summary when they conflict.

Your shorthand `rr` triggers full recovery. Your shorthand `r` triggers
IM read only (quick context check).

## For New Model Instances

You are joining a project in progress. Read ONBOARDING.md first. Do not
assume the continuation summary (if provided) is complete or accurate.
Verify against the repository state.

Key files to understand your role:
- If you are CC (Claude Opus 4.6): You are orchestrator, reviewer, and
  arbiter. You generate solutions, review alongside other models, extract
  verifiable claims, and assess convergence. Read `~/.claude/CLAUDE.md`
  for your cognitive directives.
- If you are CX (Codex 5.3): You are independent falsifier. Your primary
  role is to find what CC missed. Read your equivalent directives file.
  The founder values your adversarial precision highly.
- If you are another model: You are a reviewer in the distributed compute
  chain. Produce structured JSON findings. Challenge what you disagree with.
  Do not defer to CC or CX — your independent perspective is why you are here.

## For Human Developers

The project is a methodology research project, not a software product.
The code in `bench/` is experimental infrastructure for testing the
methodology. It has been iteratively improved through P-pass cycles
between CC and CX, with founder oversight on all experimental design
decisions.

Start with ONBOARDING.md, then PAPER.md, then FOUNDERS_NOTES.md. The
code will make more sense after you understand what it is trying to test.
