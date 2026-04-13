# Recovery Protocol

Last updated: 13 April 2026 01:26 BST

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
## Current Pending Work (13 April 2026 01:24 BST)

793 tests pass. Branch: `exp39-experimental`. Last commit: a8fb729.

**39-0 IS READY TO RUN.** Full readiness assessment completed with 4 sources (own FFF, Gemini 3.1 Pro confer, Codex 5.3 confer, 2 explore agents). None of the 10 execution order items block the infrastructure gate test. Assessment: `experimental_notes/Exp39_Readiness_Assessment_2026-04-13.md`. TTS: `~/Desktop/CDSFL_tts/Exp39_Readiness_Assessment_2026-04-13.txt`.

**FIXES APPLIED THIS SESSION (13 April 2026):**
- Fix 1: `origin_type="model"` set on all 5 Finding() instantiation sites in `bench/runner_core.py` (JSON array L417, JSON object L496, pipe-delimited L549, marker L710, fallback L734).
- Fix 2: 6 provenance fields added to `FindingRegistry.register()` in `bench/reference_runner.py` (origin_type, source_ref, retrieval_query, retrieved_at, source_hash, source_diversity).
- Fix 3: Launch path blocker fixed — `--test-article` changed from `required=True` to optional with post-parse validation, so `launch_exp39.py`'s `run --config <path>` no longer fails at argparse.
- Fix 4: `bench/macrophage_cell.py` (546 LOC) committed — missed from prior sv commit.

**CONFER ROUND 5 (Exp 39 Readiness, 13 April 2026):**
- Gemini 3.1 Pro: 8,245 chars. More conservative — recommended 5 sequential steps before 39-0. FFF falsification partially refuted most claims.
- Codex 5.3: 10,339 chars. Found launch path blocker (fixed). Confirmed enum serialization issue. Agreed 39-0 can run with small fixes.
- Confer: `bench/logs/confer_exp39_readiness/`

**IDENTIFIED BUT NOT YET FIXED (recommended before 39-0):**
1. Round report detail enhancement — counts-only to finding descriptions + provenance (~30-50 LOC in reference_runner.py). Most important for HIL review.
2. Enum serialization — CellType/ClaimType repr strings in ImmuneResponse checkpoints (~5 LOC in insect_brain.py).
3. Optional: minimal `cs_software.toml` for domain awareness (~30-50 lines TOML).

**DEFERRED UNTIL AFTER 39-0 (confirmed by readiness assessment):**
1. Domain-agnostic gate interface (IFalsificationGate protocol + GateResult)
2. Convergence gate: add churn detection (§7.1a) as C6
3. Missing domain configs (biology, info science, engineering immune, cs_software)
4. B-Cell dispatch: route to domain-specific tools from new TOML configs
5. Severity fusion (§7.7) for gate output synthesis
6. Sycophancy detection (§7.5) — can shadow alongside 39-0
7. O1 calibration: sensitivity dial, circuit breaker, semantic clustering
8. MC command sync across all reference locations
9. Phase 9 (research write-up) — deferred post-Exp 39

**LAUNCH COMMAND:** `python3 bench/launch_exp39.py --only 39-0`

**Also pending:** Onboarding script redesign (merge semantic context + automation into single executable Python file).
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
