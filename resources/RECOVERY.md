# Recovery Protocol

Last updated: 30 March 2026 07:14 UTC

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

## Current Pending Work (30 March 2026)

Experiments 12, 13a, 13b, 14 ALL COMPLETE. See ONBOARDING.md for details.

EXPERIMENT 15 Run 3 COMPLETE + LAYER 1 FIXES (30 March 2026, `148f80d`):
- 286 findings across 7 rounds, 5 models. Parser recovered +18 (tuple format).
- CX confer: 7 findings, 4 applied (DOTALL, fences, proposed_fix, watchdog).
- 4 convergent findings resolved. 350 tests passing.

EXPERIMENT 16 COMPLETE (30 March 2026, `881cf43`):
- 5-model CDSFL review of Exp 17 plan. 54 findings, 45 improvements.
- 11 convergent themes resolved: full file delivery, split blind round,
  independent stop caps, behaviour-based success criteria, fault injection,
  mandatory telemetry, SymPy for math ops, dependency-aware fix DAG.
- All 4 open questions resolved. Plan APPROVED for execution.
- Collation report: bench/logs/experiment_16/experiment_16_collation_report.md

EXPERIMENT 17 PREREQUISITES COMPLETE (30 March 2026, `e59f522`):
- Runner: bench/run_exp17_immune.py (R0A blind + R0B seeded + adaptive)
- 4 canary tests passing (empty response, false positive, cascade, oscillation)
- 5 Layer 1 preflight tests passing
- Round-level telemetry, DeepSeek decomposition, interface summary, traceability
- Independent stop caps: round 10 + wall-clock 4h
- Execute: python3 bench/run_exp17_immune.py run

ROADMAP (30 March 2026):
1. Experiment 17: execute (runner ready, `e59f522`)
3. Build immune persistence layer (JSON, ~150 lines)
4. Build Policy Engine (consolidation of remediation chains + registry)
5. Wire verification chain into live pipeline
6. Full bench run (Bench Run 2) — the finish line
7. Deferred math model items (A-D1 through A-D5) — not blocking bench
Plan: docs/experimental_notes/Immune_Persistence_And_PE_Plan_2026-03-30.txt

STOPPING CRITERION (founder-defined 30 March 2026):
"Everything wired and fully operational to an extent that we can turn it
against the bench without wasted effort. We stop when we can show the bench
produces meaningful results." Occam's razor: simplest sufficient at every
level. Do not over-engineer. Community has more compute to refine later.

META-TRAJECTORY: Problem space shrinking across experiments.
Exp12=structural breaks, Exp13=calibration, Exp14=design gaps, Exp15=edge
cases. Each iteration finds less fundamental problems. Methodology converging
on itself. Infinite iteration trap acknowledged — stop when it works as
specified, not when every edge case is handled.

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
