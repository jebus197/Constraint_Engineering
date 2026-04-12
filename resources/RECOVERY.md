# Recovery Protocol

Last updated: 12 April 2026 15:51 BST

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
## Current Pending Work (12 April 2026 15:51 BST)

762 tests pass. Branch: `exp39-experimental`. Last commit: b0f33d7.

**AIS/Holland/Kohonen Literature Assessment — COMPLETE:**
- Three research lineages assessed against CDSFL (Holland CAS, Kohonen SOMs, AIS)
- 5 integration gaps identified, ranked, and reviewed by Gemini + Codex under FFAFP
- Implementation order agreed: 3 (embeddings) → 2 (suppression) → 1 (memory) → 5 → 4

**Revised Mathematical Model — DERIVED AND CONFERRED:**
- Three modifications to R_k(i) framework proposed (embedding similarity, continuous
  suppression, persistent memory). SymPy + Wolfram verified.
- Conferred with Gemini + Codex: 3 critical errors found and verified programmatically:
  1. Suppression weight must NOT modulate q_eff (Bayesian corroboration collapse, 113x risk overestimate)
  2. Predecessor-product suppression is order-dependent (12 distinct outcomes from 24 permutations)
  3. Weighted kappa_set denominator overflows [0,1] (kappa=-2.0 under realistic conditions)
- Corrected formulation: top-k exponential suppression (order-invariant), numerator-only kappa,
  blended memory prior with drift detection. All fixes verified.
- Shadow code built: `bench/dm/_shadow_extensions.py` (credit scorecard + steering predictor)
- Bug found in shadow code: novelty_yield ignores is_novel parameter (confirmed via AST parse)

**Confer Protocol Updated:**
- All model confers now run under full CDSFL + FFAFP (revised 12 April 2026)
- Model routing: cc2=Claude Opus 4.6, cx=Codex GPT-5.4, ge=Gemini 3.1 Pro,
  cgpt=ChatGPT GPT-5.4, ds=DeepSeek Reasoner

**Exp 39 Infrastructure — BUILT AND TESTED (earlier this session):**
- All 14 sub-experiment configs, sequencer, Exp 38 fixes. 762 tests pass.

NEXT:
1. Fix shadow credit novelty_yield bug
2. Formalise corrected mathematical model in MATHEMATICAL_APPENDIX.md
3. Build embedding similarity (Gap 3) — shared backend, bounded output, dual threshold
4. Build Expert Encodings S_k integration (wire into immune pipeline, 150-200 LOC)
5. Add HIL phase gate to burst mode transitions (30-50 LOC)
6. Build Macrophage shadow-mode prototype (200-300 LOC, log only)
7. Write tests for new sub-experiment infrastructure
8. Run 39-0 (infrastructure gate), then 39-A
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
