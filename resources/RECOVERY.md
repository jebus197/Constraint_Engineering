# Recovery Protocol

Last updated: 12 April 2026 13:05 BST

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
## Current Pending Work (12 April 2026 13:04 BST)

762 tests pass. Branch: `exp39-experimental`. Last commit: 42779ad.

**Exp 38 Fixes — BUILT AND TESTED (this session):**
- D1-B: Churn-based stall convergence in `reference_runner.py`
- P4: TARGET_FILE field + inference in `dm/_types.py`, `runner_core.py` (all 4 parsers)
- Classifier: LLM primary in software domain in `immune_agents.py`
- Gemini dispatch switched to OpenRouter in `experiment_11_orchestrator.py`
  (model: `google/gemini-3.1-pro-preview`, `reasoning.effort: "high"`)
- Deprecated `google-generativeai` package uninstalled
- Statistics domain TOML configs created + 6 schema parameters added

**Exp 39 Infrastructure — BUILT AND TESTED (this session):**
- `bench/exp39_config.json` — master config, 14 sub-experiments with dependency DAG
- `bench/exp39_configs/` — all 14 configs (39-0 through 39-M)
- `bench/launch_exp39.py` — sequencer script with topological sort, gate fail-fast,
  `--only`/`--skip`/`--dry-run`/`--preflight` support
- Dry-run verified: all 14 resolve in correct dependency order
- `--only 39-D` correctly pulls 4 transitive deps (0, A, B, C)
- `--skip 39-K 39-L 39-M` correctly drops shadow experiments

**Open Brain fix:**
- `pyproject.toml` build backend corrected in OpenBrain repo. Needs commit there.

NEXT:
1. Build Expert Encodings S_k integration (wire into immune pipeline, 150-200 LOC)
2. Add HIL phase gate to burst mode transitions (30-50 LOC)
3. Build Macrophage shadow-mode prototype (200-300 LOC, log only)
4. Write tests for new sub-experiment infrastructure
5. Run 39-0 (infrastructure gate), then 39-A
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
