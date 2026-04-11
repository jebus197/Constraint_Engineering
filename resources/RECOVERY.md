# Recovery Protocol

Last updated: 11 April 2026 19:02 BST

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
7. For Exp12 analysis: read `~/Desktop/CDSFL_tts/Exp12_Final_Analysis_2026-03-29.txt`
8. For UX vision context: read `~/Desktop/CDSFL_tts/CDSFL_UX_Vision_Sketch_2026-03-28.txt`
9. **For Exp 36 ground truth and forward path:** read `experimental_notes/Exp36_Ground_Truth_Reference_2026-04-08.md` — canonical reference consolidating all findings, immune status corrections, 13 design improvements, mathematical model gaps, and resumption plan.

This is enough to resume most tasks.

<!-- SV:PENDING_START -->
## Current Pending Work (11 April 2026 19:02 BST)

762 tests pass. Exp 38 COMPLETE (wall clock cap, 24 rounds, 169 canonical).

**Exp 38 Ouroboros — COMPLETE (14:33 BST):**
- 24 rounds (R0-R23), 545 raw findings, 169 canonical. γ_final=0.510.
- Never converged. Wall clock cap at 29,503s. Phase 0 consumed entire budget.
- Closest to convergence: R21 (only blocker: contested=9).
- 59 HIL flags: CC2 21, ChatGPT 13, Codex 13, DeepSeek 7, Gemini 5.
- 6 corroborated runner bugs + 6 design findings (D1-D6) from monitoring.
- Findings: `experimental_notes/Exp38_Ouroboros_Findings_2026-04-11.md`
- Report: `bench/logs/exp38_ouroboros_20260411T041938Z/exp38_ouroboros_report.json`

**Bug: Phase 0 missing convergence overrides (CRITICAL):**
Burst mode active (6 phases + integration) but `phase_convergence_overrides()`
only applied at phase transitions (line 2831). Phase 0 runs with base config
(`earliest_stop_round: 12`), not per-phase override (round 3).
Phase 0 consumed entire 24-round budget. Phases 1-5 never reached.

**Runner bugs found by model panel (6 corroborated):**
1. `_compute_rho()` early return on zero raw (sev 0.95)
2. `contested_count()` wrong unresolved-challenge logic (sev 0.93)
3. `open_crit_high_count()` missing REOPENED status (sev 0.93)
4. `_compute_rho()` off-by-one (sev 0.91)
5. `RunnerConfig.__post_init__` silent override (sev 0.90)
6. `contested_count()` hardcoded grace period (sev 0.85)

**Design findings from monitoring (D1-D6):**
- D1: Churn detection without adaptive response
- D2: Contested timeout and HIL escalation needed
- D3: z3 grounding works for config-space claims (R22 proof)
- D4: MERGE deadlock accumulation (12+ findings permanently deferred)
- D5: Gemini UNSTRUCTURED finding format degradation
- D6: DeepSeek chunk delivery failures

**Parser/pipeline bugs:**
- P1: ~75% findings lack SEARCH/REPLACE blocks → S_k ESCALATE
- P2/P3: Gemini V-prefix / no TARGET_FILE → UNEVALUABLE
- Regex classifier ~15% agreement with LLM (fundamentally broken for code)

**Phase B schema design (deferred):**
Per-schema-element convergence. Distinct from code-structure burst decomposition.

NEXT (Exp 39 fix list, ordered by impact):
1. Fix Phase 0 convergence override bug (CRITICAL)
2. Fix 6 corroborated runner bugs
3. Implement D2: contested timeout + HIL escalation
4. Implement D1: churn feedback mechanism
5. Strengthen SEARCH/REPLACE parser (P1)
6. Fix confirmation-finding parser (P2/P3)
7. Address D4: MERGE deadlock arbitration
8. Replace/calibrate regex classifier
9. Uninstall deprecated google-generativeai
10. Run Exp 39 with all fixes on same target
<!-- SV:PENDING_END -->

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
