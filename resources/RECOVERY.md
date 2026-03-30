# Recovery Protocol

Last updated: 30 March 2026 17:05 UTC

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

## Current Pending Work (30 March 2026, 22:59 UTC)

Experiments 12–16 ALL COMPLETE. See ONBOARDING.md for details.

EXPERIMENT 17 RUNNING (30 March 2026):
- Resumed after Gemini spending cap fix + CX prompt efficiency confer.
- R0A (177 findings) + R0B (204 findings) + Round 2 (150 findings) from cache.
- Round 3 LIVE: Immune (31 findings) + Load Balancing (38 findings) complete.
  Persistence + Math Model in progress. All 5 models active.
- CX sub-area escalation and DeepSeek feasibility gate both firing correctly.
- Log: `bench/logs/experiment_17/run_output_r7.log`
- Confer record: `docs/experimental_notes/Dispatch_Fix_Confer_2026-03-30.md`

EXPERIMENT 18 RUNNER BUILT (30 March 2026, `e11b4a2`):
- bench/run_exp18_confer.py — sequential confer (Whole Body Phase 1+2).
- Attributed findings, fingerprint dispatch ordering, NOVEL/VALIDATION/CHALLENGE.
- Pending: preflight + canary, then launch after Exp 17 collation.

WHOLE BODY ARCHITECTURE DESIGNED (30 March 2026):
- docs/experimental_notes/Whole_Body_Architecture_Plan_2026-03-30.md
- Nervous (dispatch sequencing), circulatory (attributed findings), endocrine
  (adaptive pacing). Exp 18 = Phases 1+2. Phases 3+4 = future.

CX PROMPT EFFICIENCY CONFER COMPLETE (30 March 2026, `8c1dacb`):
- CX burns 155K tokens on 78 tool calls investigating codebase instead of
  producing findings. Fix: 6-field standard confer packet with embedded code,
  stdin piping, output-schema. 78% token reduction proven. ALL IMPLEMENTED.
- Record: `docs/experimental_notes/CX_Prompt_Efficiency_Confer_2026-03-30.md`

TTS OUTPUT PROTOCOL UPDATED (30 March 2026):
- New `tts-output-protocol` directive in CLAUDE.md replaces old tts-default-on
  + tts-repo-mirror. Per-project Desktop folders (e.g. `CDSFL_tts/`) + repo
  `experimental_notes/` as formatted .md. 141 files moved from Accessibility/.

ROADMAP (30 March 2026):
1. ~~Implement confer packet fixes in orchestrators~~ DONE (`8c1dacb`)
2. Exp 17 running → collate findings → integrate fixes
3. Test + launch Experiment 18 (sequential confer)
4. Build immune persistence layer (JSON, ~150 lines)
5. Build Policy Engine (consolidation of remediation chains + registry)
6. Wire verification chain into live pipeline
7. Full bench run (Bench Run 2) — the finish line
8. Deferred math model items (A-D1 through A-D5) — not blocking bench

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
