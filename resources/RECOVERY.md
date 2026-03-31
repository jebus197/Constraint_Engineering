# Recovery Protocol

Last updated: 31 March 2026 11:46 UTC

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

## Current Pending Work (31 March 2026, 01:11 UTC)

Experiments 12–16 ALL COMPLETE. See ONBOARDING.md for details.

EXPERIMENT 17 PAUSED (31 March 2026):
- Round 3 COMPLETE (140 findings). Round 4 partial (Immune 34, LB 36,
  Persistence 26 complete; Math Model partial — CX hit usage limit mid-round).
- CX OpenAI usage limit exhausted (~3h runtime). Resets ~3 April.
- CX efficiency confer R2: 4 models × 2 rounds, 46 findings, converged.
- CLI efficiency fixes IMPLEMENTED in call_codex(): reasoning effort
  xhigh→medium, MCP servers disabled, plugins disabled, ephemeral mode.
- Log: `bench/logs/experiment_17/run_output_r7.log`
- Confer results: `bench/logs/cx_efficiency_confer_r2/`

EXPERIMENT 18 RUNNER BUILT (30 March 2026, `e11b4a2`):
- bench/run_exp18_confer.py — sequential confer (Whole Body Phase 1+2).
- Attributed findings, fingerprint dispatch ordering, NOVEL/VALIDATION/CHALLENGE.
- Pending: preflight + canary, then launch after Exp 17 collation.

WHOLE BODY ARCHITECTURE DESIGNED (30 March 2026):
- docs/experimental_notes/Whole_Body_Architecture_Plan_2026-03-30.md
- Nervous (dispatch sequencing), circulatory (attributed findings), endocrine
  (adaptive pacing). Exp 18 = Phases 1+2. Phases 3+4 = future.

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

GEMINI PHASE 1 MATH AUDIT COMPLETE (31 March 2026, `d139e12`):
- decomposed_dispatch.py BUILT (reusable multi-turn staged context loading)
- gemini_math_audit.py: 8-chunk decomposed delivery, all 8 WAITING responses clean
- 14,872 chars of mathematical analysis, 174s total
- KEY FINDINGS: 14 symbol collisions (namespace refactor HARD), all 5 deferred
  items resolved, A-N1 anti-parroting REJECTED (contradicts O_A), A-N3 modified,
  Ising model rejected, decomposed delivery attention claim FALSIFIED (cumulative
  context means α(L_total) applies at synthesis regardless of chunking)
- Proposes §9-§11 structure for composition extensions
- Log: bench/logs/gemini_math_audit/round0_gemini_20260331T102313Z.json

ROADMAP (31 March 2026, updated 11:46 UTC):
1-3. ~~Confer packets, CX CLI, composer~~ ALL DONE
4. ~~MM_F001 + MM_F002 applied~~ DONE (`d139e12`)
5. ~~decomposed_dispatch.py built~~ DONE (`d139e12`)
6. ~~Gemini Phase 1 math audit~~ DONE (`d139e12`)
7. SymPy verify Gemini's claims (14 collisions, deferred item resolutions)
8. Phase 2: all-model CDSFL review of Gemini output (tight math box, decomposed)
9. Iterate until convergence (SymPy + model agreement)
10. Apply remaining Exp 17 implementation fixes (IM_F001-F013, LB, VC)
11. Wire composer into orchestrator
12. Resume Exp 17 (CX quota resets ~3 Apr)
13. Exp 19: composable directive hypothesis test
14. Test + launch Experiment 18 (sequential confer)
15. Build immune persistence + Policy Engine
16. Full bench run (Bench Run 2) — the finish line

STOPPING CRITERION (founder-defined): "Everything wired and fully operational
to an extent that we can turn it against the bench without wasted effort."

META-TRAJECTORY: Exp12=structural, Exp13=calibration, Exp14=design gaps,
Exp15=edge cases, Exp16=plan review, Exp17=immune+LB live, Exp18=confer.

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
