# Recovery Protocol

Last updated: 13 April 2026 18:51 BST

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
## Current Pending Work (13 April 2026 18:50 BST)

793 tests pass. Branch: `exp39-experimental`. Last commit: d54a8e6.

**EXP 39-0 COMPLETE — CONFOUNDED.** R_k adoption data invalid. Three confounds:
(C1) User prompt missing R_k mandate, (C2) payload 4.6× decomposition threshold,
(C3) monolithic dispatch to 3/5 models. Bug findings may be valid.
Full analysis: `experimental_notes/Exp39_Confound_Analysis_2026-04-13.md`

**FIXES APPLIED THIS SESSION (13 April 2026):**
- `_build_prompt()` in reference_runner.py: added ANALYSE, FALSIFICATION (MANDATORY),
  CORROBORATION (MANDATORY) — matching Exp 37's 10-field schema. This was the primary
  confound (user prompt didn't ask for R_k despite system prompt mandating it).
- Exp 39-0 marked as confounded in ONBOARDING.md and experimental notes.
- Prior session fixes still in place: operational directive loading, per-round metrics
  injection, decomposed dispatch FFAFP+R_k, provider fix.

**LESSONS-FORWARD AUDIT — 7 STILL MISSING:**
4. Semantic novelty feedback (3 graduated signals from Exp 37)
6. Prior fix summary context (`_build_prior_fix_summary()` from Exp 37)
7. Consolidation phase for final 3 rounds (Exp 36 Ground Truth, HIGH)
8. Per-model ρ tracking with targeted ITC (Exp 36 Ground Truth, HIGH)
9. Context windowing for long runs (Exp 36 Ground Truth, HIGH)
10. S_k format pre-check with reformat request (Exp 38)
11. Parser fixes P2/P3 — CC2 finding leak, Gemini verdict extraction (Exp 38)

**FINGERPRINT GAP:** Attention metrics (measured_attention_span, compression_threshold,
quality_at_capacity) all null. Data exists in checkpoint logs (parse_yield per model
per round). Extraction pipeline not built. `burst_planner.py` D_decay condition exists
but never fires because D_decay is never populated.

**TEST ARTICLE DESIGN ERROR:** 10/14 Exp 39 sub-experiments target reference_runner.py
(163K chars). Only 39-H uses evidence.py (23K). Domain decomposition happened; article
size decomposition did not. Sub-experiment configs need redesign.

**IMMEDIATE NEXT STEPS:**
1. Dynamic decomposition: payload > LENGTH_THRESHOLD (80K) → decompose all models
2. Redesign Exp 39 sub-experiment test articles for appropriate sizes
3. Wire fingerprint attention metrics from checkpoint data
4. Carry forward remaining 7 lessons
5. Re-run gate test with fixes in place (evidence.py or appropriately-sized target)

**DEFERRED (architecture items for 39-A onwards):**
1. Domain-agnostic gate interface (IFalsificationGate protocol + GateResult)
2. Convergence gate: add churn detection (§7.1a) as C6
3. Missing domain configs (biology, info science, engineering immune, cs_software)
4. B-Cell dispatch: route to domain-specific tools from new TOML configs
5. Severity fusion (§7.7) for gate output synthesis
6. Sycophancy detection (§7.5)
7. O1 calibration: sensitivity dial, circuit breaker, semantic clustering
8. MC command sync across all reference locations
9. Phase 9 (research write-up) — deferred post-Exp 39
10. Implementation plan: `~/.claude/plans/effervescent-watching-platypus.md`
11. Prompt schema as first-class tested artefact (not string literal in 3700-line file)

**Also pending:** Onboarding script redesign.
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
