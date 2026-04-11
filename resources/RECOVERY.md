# Recovery Protocol

Last updated: 11 April 2026 00:35 BST

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
## Current Pending Work (11 April 2026 00:35 BST)

Experiments 12–? ALL COMPLETE. 501/502 tests pass (1 known failure, see below).

**3-Layer DC v2 Classification Fix (10–11 April 2026):**
Exp 38 R0 revealed 17/26 code findings misrouted to MATHEMATICAL (operators in
code descriptions) and 3/26 defaulted to UNCATEGORISED. Implemented 3-layer fix:
- **Layer 1:** Domain-aware code-context regex (`_CODE_CONTEXT_PATTERN`) checked
  BEFORE math pattern. Strong-math veto (`_STRONG_MATH_SIGNAL`) preserves genuine math.
- **Layer 2:** Targeted LLM classifier for UNCATEGORISED residue only (15s timeout,
  fail-open, confidence threshold 0.55).
- **Layer 3:** Domain TOML loading + hard verification gate (nothing exits without
  at least one tool-grounded verdict from CT, B-Cell, or NK).
- **CX confer fixes (CX-F1/F2):** Removed bare-word branches from `_CODE_CONTEXT_PATTERN`
  (matched math vocabulary). Added 6 terms to `_STRONG_MATH_SIGNAL`.
- **24 new tests** in `bench/tests/test_immune_agents.py`.

**Known failure:** `test_cx_f1_math_with_function_word_not_misrouted` — strong-math
signal ("bounded") is only checked inside code-context branch, not as independent
promoter. Fix identified: add strong-math promotion gate before software fallback
(step 5.5). NOT YET APPLIED — pending discussion.

Uncommitted changes in working tree:
  M bench/endocrine.py
  M bench/immune_agents.py
  M bench/insect_brain.py
  M bench/logs/immune_shadow.log
  M bench/reference_runner.py
  M bench/tests/test_endocrine.py
  M bench/tests/test_exp29_integration.py
  M bench/tests/test_immune_agents.py
  M docs/CURRENT_STATE.md
  M resources/ONBOARDING.md
  M resources/RECOVERY.md
  ?? bench/logs/confer_dc_fix_cx_20260410T215131Z.txt
  ?? bench/tests/test_runner_status_transitions.py
  ?? experimental_notes/DC_v2_3Layer_Confer_2026-04-10.md
  ?? experimental_notes/Exp38_Fix_Cycle_2026-04-10.md

Remote: up to date.

NEXT:
1. Apply strong-math promotion gate fix (Option 1 from analysis — 1 line in
   `_classify_claim_v2`, step 5.5 before software fallback)
2. Re-run tests — expect 502/502 pass
3. Commit all changes (17 runner/endocrine/immune fixes + 3-layer classification
   fix + CX-F1/F2 confer fixes + 24+ new tests + confer logs)
4. Push to origin
5. Restart Exp 38 from R0 with 3-layer classification active
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
