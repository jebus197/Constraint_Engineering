# Recovery Protocol

Last updated: 11 April 2026 09:45 BST

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
## Current Pending Work (11 April 2026 09:45 BST)

762 tests pass. Exp 38 live run in progress (PID 15636, started 04:19 BST).

**Exp 38 Ouroboros — LIVE (R7 in progress):**
- R0–R6 complete. R7 immune pipeline running. 99 total canonical findings.
- γ=0.377 (R6), ρ_avg=0.131 (R7). ITC threshold 0.25 crossed at R4.
- R6 was CC2-only dispatch. R7 resumed full 5-model. Novelty burst in R7 (9 novel).
- 7 findings closed. 5 persistently ADMISSIBLE. 2 z3-CONFIRMED.
- Findings collation: `experimental_notes/Exp38_Ouroboros_Findings_2026-04-11.md`
- TTS version: `~/Desktop/CDSFL_tts/Exp38_Ouroboros_Findings_2026-04-11.txt`
- 6 parsing issues documented (P1–P6). P1 (SEARCH/REPLACE format) is HIGH priority.

**Uncommitted changes in working tree (pre-experiment fixes):**
  M bench/immune_agents.py — logger rename, WP3c/WP3d fixes
  M bench/runner_core.py — chevron regex fix
  M bench/logs/immune_shadow.log — log output
  ?? bench/launch_exp38.sh — experiment launch script
  ?? bench/logs/exp38_live_output.log — live output
  ?? bench/logs/exp38_ouroboros_20260411T041938Z/ — checkpoint + responses
  ?? bench/logs/immune_pipeline.log — pipeline log
  ?? experimental_notes/Exp38_Ouroboros_Findings_2026-04-11.md — findings

Remote: ahead by 4.

**Deferred fixes (do after experiment):**
1. `pip3 uninstall google-generativeai` — deprecated package causing FutureWarning
2. Cosmetic: "below threshold 0.70" log text when MATHEMATICAL guard is the real reason

**Architectural gap identified by founder:**
Runner lacks per-element convergence. Current ITC tracks one global ρ_avg.
Founder wants per-element convergence (mathematical model, immune pipeline, registry,
policy engine each converge independently). This would require:
- Finding taxonomy layer (target component, not just flaw type)
- Per-element ρ/γ computation
- Per-element convergence gates
This is a meaningful extension for Phase B, not a quick fix.

NEXT:
1. Let Exp 38 complete (or kill if not useful — ρ_avg oscillating, global convergence at R12+)
2. Fix P1–P4 parsing issues before Bench Run 2
3. Commit all pre-experiment fixes + experiment outputs
4. Consider per-element convergence design for next runner iteration
5. Uninstall deprecated google-generativeai
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
