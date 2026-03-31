# Recovery Protocol

Last updated: 31 March 2026 21:56 UTC

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

## Current Pending Work (31 March 2026, 21:56 UTC)

Experiments 12–18 ALL COMPLETE. See ONBOARDING.md for details.

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

NEXT STEPS (31 March 2026):
1. Standard CDSFL confer baseline (existing schema, no novel changes) with
   CC2 + CX + Gemini on immune task area. FFF via situation layer. Sequential
   dispatch. This validates all Exp 17/18 code fixes under live multi-model review.
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
