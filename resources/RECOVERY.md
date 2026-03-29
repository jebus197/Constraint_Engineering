# Recovery Protocol

Last updated: 29 March 2026 06:46 UTC

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

## Current Pending Work (29 March 2026)

Experiment 12 COMPLETE. All fixes implemented and confer-reviewed.
Experiment 13a (confer round) COMPLETE. Experiment 13b (live run) IN PROGRESS.

Post-Exp12 fixes implemented (all committed, 177 tests passing):
- Vocabulary saturation stop signal (d52526a)
- Windowed fingerprint replacing EMA (d52526a)
- Model restart logic — IT Crowd principle (9f3d9e4)
- Adaptive decomposition per model (9f3d9e4)
- Artifact-size-based max_rounds with ceiling of 30 (9f3d9e4, cd023d9)
- Fingerprint blending on restart (806162a)
- Per-model mu computation — CC2 approved HARD (c91d63c, f5b457e)

Exp13a confer synthesis: 3 modifications applied, 4 approved, 1 deferred.
- Fix 3: restart guard now per-model (cd023d9)
- Fix 5: max_rounds ceiling of 30 (cd023d9)
- Fix 1: monotonic-decrease documented (cd023d9)

Documentation updated:
- EXPERIMENTAL_RESULTS.md: Experiment 12 full write-up (35471eb)
- FOUNDERS_NOTES.md: "The Live Wire" + biodiversity reassessment (35471eb)
- README.md: extended to 29 March — dynamic management, live orchestration,
  cognitive modes, synthetic domain expert thesis (35471eb)
- Shorthand fix: cy = continue, t = TTS only (35471eb)

Experiment 13b COMPLETE + FULLY ANALYSED (29 March 2026): 4 rounds, 184
findings parsed. 5/5 models survived. Terminated via CONVERGED. Full
statistical analysis: Kruskal-Wallis H=44.74 (p<0.0001) on cross-model
severity. Gemini (0.818) and Codex (0.785) produce highest-severity findings.
Duane NHPP fit R²=0.9999. Models independently found 97 findings in 7/8 fix
areas. Premature termination diagnosed via SymPy/Wolfram: decomposed dispatch
× vocab saturation interaction (Heaps' law, β≈0.024). Full entry in
EXPERIMENTAL_RESULTS.md. TTS: Exp13b_Full_Analysis_2026-03-29.txt.

Self-adaptive CDSFL analysis COMPLETE (29 March 2026): Three-tier architecture
P-passed. DeepSeek dual pathology: dispatch blocking + verification
miscalibration (0% verified, 6/15 corroborated TRUE by peers, 2σ outlier).
Three new immune pathology types designed. Registry Layer 4 (per-model TOML)
exists but not wired — Phase A. Implementation: Phases A-E. Novelty trajectory
confirmed ascending (5 independent signals). TTS exports:
Exp13b_What_The_Models_Found, Exp13b_Context_Novelty_Methodology,
Self_Adaptive_CDSFL (all 2026-03-29).

Next priorities:
1. Implement Phase A: wire per-model registry into orchestrator
2. Implement Phase B: close immune feedback loop (Tier 1 auto-adjustment)
3. Recalibrate vocab saturation for Exp14 (τ 0.10→0.03-0.05, W 3→5)
4. Resolve deferred math model items (A-D1 through A-D5)
5. Outreach emails to industry specialists

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
