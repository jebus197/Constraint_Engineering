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
- Testable as Exp 19 condition or Bench Run 2 variant.
- Also flagged: seeded sensitivity + NMI sycophancy trigger for evaluation.

ROADMAP (31 March 2026, updated 14:28 UTC):
1-9. ~~All confer/composer/audit work~~ ALL DONE (converged)
10. Apply CX's two minor modifications to Gemini Round 6 text
11. Apply converged model to MATHEMATICAL_APPENDIX.md (§9, §10, namespace, C(n))
12. Apply remaining Exp 17 implementation fixes (IM_F001-F013, LB, VC)
13. Wire composer into orchestrator
14. Resume Exp 17 (CX quota resets ~3 Apr)
15. Exp 19: composable directive hypothesis test (include find-fix-follow condition)
16. Test + launch Experiment 18 (sequential confer)
17. Build immune persistence + Policy Engine
18. Full bench run (Bench Run 2) — the finish line

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
