# Recovery Protocol

Last updated: 30 March 2026 02:50 UTC

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

EXPERIMENT 15 IN PROGRESS (30 March 2026):
- Live wire: dynamic_management.py (~6,100 lines), 5 models, self-adaptive
  immune layer (Level 3) active.
- Run 3 in progress (Round 1, 21 findings). Runs 1-2 killed by DeepSeek
  circuit breaker — fixed mid-experiment.
- Commits this session:
  - c67ed97: Self-adaptive immune layer with extended P-pass (Level 3)
  - 27e3622: Autonomous remediation engine + human-in-the-loop safety gate
  - aa89585: CircuitBreakerTripped catch (no longer kills experiment)
  - 5058d29: DeepSeek empty response retry with halved max_tokens
  - df52e85: Dual-track failure mode fixes (§2 math model + 3 new detectors)
- 253 tests passing.

FAILURE MODE ANALYSIS COMPLETE (30 March 2026):
6 failure modes classified from Exp15 evidence:
1. Kappa on empty sets (math model: φ_i format yield)
2. CoT budget exhaustion (math model: f_del + immune: already fixed)
3. Cascade degradation (immune: monotonic decline detector)
4. Parser format divergence (immune: parser yield anomaly detector)
5. Efficiency collapse (immune: cost-per-finding spike detector)
6. Decomposition overshoot (math model: η_dec decomposition yield bounds)

ROADMAP (founder-approved 30 March 2026):
1. Complete Exp15 Run 3 iteration
2. Run Experiment 16 if new failure modes emerge
3. Build immune persistence layer (JSON, ~150 lines)
4. Build Policy Engine (consolidation of remediation chains + registry)
5. Full bench run with accumulated immune memory
6. Resolve deferred math model items (A-D1 through A-D5)
Plan: docs/experimental_notes/Immune_Persistence_And_PE_Plan_2026-03-30.txt

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
