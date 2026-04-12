# Recovery Protocol

Last updated: 12 April 2026 02:03 BST

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
## Current Pending Work (12 April 2026 02:01 BST)

762 tests pass. Branch: `exp39-experimental`. All changes uncommitted.

**Exp 39 Runner Fixes — BUILT, TESTED, CONFERRED (not yet committed):**
- 22+ fixes from Exp 38 findings implemented in `reference_runner.py` (+280 lines),
  `runner_core.py` (+86 lines), `immune_agents.py` (+28 lines).
- z3 formal verification: 7/7 proofs pass.
- 3 rounds of adversarial confer (Gemini + Codex). No actionable findings from Round 3.
- Key architectural changes:
  - Dynamic context budgets (measured performance, not vendor claims)
  - Adaptive per-model ITC parse yield detection (rolling baseline, hard floor)
  - Quality Collapse Spiral fix (quality gate on prompt_chars_history)
  - Fingerprint semantic error fixed (response length mislabeled as context chars)
  - DRY fix: threshold computed once in _itc_detect, read by fingerprint gate
  - Documentation: Q1 trend-blindness, Q4 ordering invariant, Q5 anti-gaming in ARCHITECTURE.md

**Exp 39 Scope Refinement (12 April 2026):**
- IN SCOPE: fix verification (done), Expert Encodings S_k integration (150-200 LOC),
  HIL phase gate between burst phases (30-50 LOC), Gemini → OpenRouter switch (~10 LOC).
- SHADOW: Macrophage cell prototype (200-300 LOC, log only, no pipeline effect).
- DEFERRED: single system/distributed compute (post-BR2), math model extension (after data),
  domain cell build-out (after domain encodings exist).
- Analysis: `experimental_notes/Exp39_Scope_Refinement_2026-04-12.md`

**Open Brain fix:**
- `pyproject.toml` build backend corrected (`setuptools.build_meta`). Package installs.
  Change is in OpenBrain repo, needs separate commit there.

NEXT:
1. Commit all Exp 39 fixes on exp39-experimental branch
2. Build Expert Encodings S_k integration (wire Python encoding into immune pipeline)
3. Add HIL phase gate to burst mode transitions
4. Switch Gemini dispatch to OpenRouter (verify quality first)
5. Macrophage shadow-mode prototype (web search cell, log only)
6. Run Exp 39 on same target (bench/reference_runner.py)
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
