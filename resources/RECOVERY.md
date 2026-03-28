# Recovery Protocol

Last updated: 28 March 2026 19:30 UTC

How to rebuild full working context from the repository alone after a
session loss, compaction event, or fresh start with a new model instance.

## Minimum Recovery (2 minutes)

1. Read `resources/ONBOARDING.md` — current project state, architecture,
   key concepts
2. Run `git log --oneline -10` — what changed recently
3. Run `git status` — any uncommitted work
4. Check if bench test is running: `ps aux | grep run_round_robin`
5. If resuming Experiment 11: read `bench/EXECUTION_PLAN_EXPERIMENT_11.md`
6. If resuming meta-test fix work: read `~/.claude/plans/agile-wondering-hejlsberg.md`
7. For UX vision context: read `~/Desktop/Accessibility/CDSFL_UX_Vision_Sketch_2026-03-28.txt`

This is enough to resume most tasks.

## Current Pending Work (28 March 2026)

Persistence layer BUILT (bench/verification_chain.py, 790 lines, 97 tests).
Distributed compute protocol was not followed — founder chose to prioritise
efficient build over clean test. Specialised subtasks instead of blind rounds.
Output correct, process not citable as clean distributed compute test but
generated an observation about CDSFL boundaries in mixed-ability environments.
Documented as Experiment 10. Protocol document: bench/DISTRIBUTED_COMPUTE_PROTOCOL.md.

Experiment 11 execution plan COMPLETE and committed (bench/EXECUTION_PLAN_EXPERIMENT_11.md).
Five-model distributed compute test: CC1 as collator, CC2 as player manager,
Codex/ChatGPT/Gemini/DeepSeek as participants. Circuit breaker, preflight
verification, 17 lessons applied, UX readiness design constraint. Awaiting
founder approval to execute.

UX vision sketch saved to ~/Desktop/Accessibility/CDSFL_UX_Vision_Sketch_2026-03-28.txt.
Three surfaces: Orchestration Console, Registry/Group Policy Editor, Domain
Configuration Manager. Registry/policy engine exists (bench/cdsfl_registry/,
4-layer hierarchy, monotonicity enforcement). Task layer and runtime layer
separation still needed. UX build follows Experiment 11.

Next: (1) Founder approves Experiment 11 plan. (2) Build OpenRouter calling
function and task brief. (3) Execute Experiment 11. (4) Build UX on the
resulting orchestration module. The persistence layer re-run is subsumed —
the five-model test is the stronger test.

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
