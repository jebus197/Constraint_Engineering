# Recovery Protocol

Last updated: 10 April 2026 14:05 BST

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
## Current Pending Work (10 April 2026 14:05 BST)

Experiments 12–37 ALL COMPLETE. 690 tests pass.

EXP 38 ROUND 0 COMPLETE — PAUSED (10 April 2026 14:05 BST):
  Target: bench/reference_runner.py, star, 5 models, burst mode (5 phases).
  26 findings, 14 confirmed by HIL verification (70% true positive).
  Paused to fix immune/endocrine gaps before restart.
  Logs: bench/logs/exp38_ouroboros_20260410T122030Z/
  Full verification: experimental_notes/Exp38_R0_Verification_2026-04-10.md

Uncommitted changes in working tree:
  M bench/directives/software/software_python_sk.txt
  M bench/directives/universal/cdsfl_operational.md
  M bench/directives/universal/expert_encoding_template.md
  M bench/logs/immune_shadow.log
  M bench/reference_runner.py
  M bench/runner_core.py
  M experimental_notes/Exp38_Plan_2026-04-09.md
  ?? bench/burst_planner.py
  ?? bench/confer_exp38_fitness.py
  ?? bench/confer_exp38_fix_review.py
  ?? bench/exp38_config.json
  ?? bench/logs/confer_exp38_fitness/
  ?? bench/logs/confer_exp38_fix_review/
  ?? bench/logs/exp38_ouroboros_20260410T104416Z/
  ?? bench/logs/exp38_ouroboros_20260410T122030Z/
  ?? bench/monitor_exp38.sh
  ?? experimental_notes/Sk_What_It_Means_2026-04-09.md

Remote: up to date.

NEXT STEPS:
  1. Fix endocrine SEARCH/REPLACE parser (wire runner's parse_search_replace_blocks).
  2. Fix _find_target_file fallback (CC2 target file = None).
  3. Promote Formalisation Agent from shadow to active.
  4. Add SymPy verification pathway for B-Cell math claims.
  5. Decide which of the 14 confirmed runner bugs to fix before restart.
  6. Restart Exp 38 from Round 0 with fixed immune/endocrine pipeline.
  7. On successful convergence: commit all changes.
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
