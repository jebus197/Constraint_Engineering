# Recovery Protocol

Last updated: 13 April 2026 17:36 BST

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
## Current Pending Work (13 April 2026 17:35 BST)

793 tests pass. Branch: `exp39-experimental`. Last commit: 2f8f8bc.

**EXP 39-0 COMPLETE.** 4 rounds, 78 findings, 35 canonical, γ=0.798. Status INCOMPLETE
(convergence gate never fired). Logs: `bench/logs/exp39_0_gate_20260413T054642Z/`.

**UNCOMMITTED CHANGES (working tree dirty):**
- `bench/decomposed_dispatch.py` — full FFAFP+R_k per-chunk/synthesis instructions
  for OpenRouter and DeepSeek decomposed dispatch paths. 6 mandatory sections:
  FIND, FOLLOW, ANALYSE, FIX, FALSIFICATION (FALSIFIER/ATTEMPT/RESULT),
  CORROBORATION (numerical R_k). Meta SRP included.
- `bench/reference_runner.py` — operational directive loading at module level,
  appended to composer phenotype in _dispatch_single_model. Per-round metrics
  injection (γ, ρ, ρ̄₃, registry counts) before each round dispatch.
- `bench/run_benchmark.py` — `claude-code` and `claude-code-thinking` providers
  using `claude -p` subprocess (Max subscription auth, no API key needed).
  See `bench/CLAUDE_CODE_PROVIDER_FIX.md`.
- Fingerprints (all 5 models), experiment logs, immune pipeline log, exp39 config.

**KEY FINDING — OSCILLATING R_k COMPLIANCE:**
R_k adoption is stochastic across rounds. No model sustained CORROBORATION across
all post-fix rounds. CC2: 5→3→0. Codex: 0→1→8. ChatGPT: 0→3→0. Gemini: 0→0→3.
Instruction-level enforcement is necessary but insufficient. Structural enforcement
(PE-level gate, runner-side validation) needed to reach Exp 37's 88-100% baseline.
This is the 0-13% falsification compliance problem demonstrated empirically.

**IMMEDIATE NEXT STEPS:**
1. Commit working tree (this sv)
2. Analyse oscillating R_k — determine structural enforcement mechanism
3. Consider adding Gemini to `pre_decompose_models` for large test articles
4. DeepSeek reasoning budget investigation (0 chars per chunk, synthesis overflow)

**DEFERRED (architecture items for 39-A onwards):**
1. Domain-agnostic gate interface (IFalsificationGate protocol + GateResult)
2. Convergence gate: add churn detection (§7.1a) as C6
3. Missing domain configs (biology, info science, engineering immune, cs_software)
4. B-Cell dispatch: route to domain-specific tools from new TOML configs
5. Severity fusion (§7.7) for gate output synthesis
6. Sycophancy detection (§7.5) — can shadow alongside future experiments
7. O1 calibration: sensitivity dial, circuit breaker, semantic clustering
8. MC command sync across all reference locations
9. Phase 9 (research write-up) — deferred post-Exp 39
10. Comprehensive implementation plan: `~/.claude/plans/effervescent-watching-platypus.md`
    (Phases 0-9: kappa fix, embeddings, suppression, memory, FFAFP docs, B4 wiring,
    O1 shadow, appendix expansion, research write-up)

**Also pending:** Onboarding script redesign (merge semantic context + automation).
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
