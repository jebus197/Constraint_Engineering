# CDSFL Project Onboarding

Last updated: 27 March 2026

Read this document first if you are a new model instance, a new developer,
or a reviewer picking up this project for the first time.

## What This Project Is

CDSFL (Constraint-Driven Synthesis and Falsification) is a methodology for
making AI-assisted technical work more reliable. It formalises the scientific
method — specifically Popperian falsification — as a structured protocol that
AI models follow when producing and reviewing technical output.

The project is approximately 13 days old (first commit: 14 March 2026). It
was built by a single founder (George Jackson) working with Claude Opus 4.6
as primary collaborator and OpenAI Codex 5.3 as independent falsifier, with
DeepSeek V3.2, Gemini 3.1 Pro, and ChatGPT 5.4 as additional review models.

**Repository:** `github.com/jebus197/Constraint_Engineering`
**Local path:** `/Users/georgejackson/Developer_Projects/Constraint_Engineering/`

## Current State (update after each major milestone)

- **First full bench test running (Run 1)** — 27 tasks x 4 conditions = 108
  runs, 5 models per run. ~78 of 108 runs complete as of 27 March.
  Run resumed from checkpoint after CX quota issue (switched to API key auth).
  This run has known confounds (see below and BENCH_RUN_1_ANALYSIS.md).
  It measures distributed compute effectiveness, not full CDSFL.
  A corrected Run 2 is planned with bare-metal model parity (claude --bare,
  OpenRouter for ChatGPT), iterative HIL, full SymPy verification, enhanced
  research pipeline (arXiv MCP, Sci-Hub, CX delegation).
- **Experimental design:** 2x2 factorial — Control (no methodology),
  HIL (expert hint only), CDSFL (structure + verification), CDSFL+HIL (full
  methodology with expert guidance and research)
- **Key distinction:** Control and HIL use self-iteration (each model
  re-examines independently, no cross-model exchange). CDSFL and CDSFL+HIL
  use confer rounds (models review each other's findings). Confer is the
  distributed compute feature being tested.
- **Verification:** SymPy (OSS) auto-verifies mathematical claims. CC
  extracts verifiable claims from raw findings when models don't provide them.
- **Policy engine:** Hierarchical Constraint Editor (CE) with 5 layers:
  universal, domain, task, model, runtime.
- **Domain expert configs:** First configs produced — portable, three-layer
  (methodology + domain + personalisation). See `configs/`.

## Smoke Test Results (24 March 2026)

The corrected experimental design produced:
- Control: 10 unique HARD findings (5 rounds self-iteration)
- HIL: 2 unique HARD findings (5 rounds self-iteration)
- CDSFL: 29 unique HARD findings (5 rounds confer)
- CDSFL+HIL: 43 unique HARD findings (5 rounds confer)

Gradient: HIL (2) < Control (10) < CDSFL (29) < CDSFL+HIL (43)

## Architecture Overview

```
Constraint_Engineering/
  PAPER.md                    -- Canonical technical statement (white paper)
  README.md                   -- Operational front door
  configs/                    -- Domain expert configurations (tradeable assets)
    examples/                 -- Methodology, software engineering, template
  docs/
    FOUNDERS_NOTES.md         -- Chronological design observations
    EXPERIMENTAL_RESULTS.md   -- All experimental data including failures
    EXTENDED_RATIONALE.md     -- General-audience companion
    MATHEMATICAL_APPENDIX.md  -- Mathematical extensions
  bench/
    run_round_robin.py        -- Main bench test orchestrator (~3500 lines)
    cdsfl_registry/           -- Constraint Editor (CE) policy engine
      registry.py             -- 5-layer hierarchical merge with monotonicity
      refinements.py          -- Independence-aware confirmation, tuple canon
      universal.toml          -- Layer 1 (immutable HARD constraints)
      domains/                -- Layer 2 (domain-specific policies)
      models/                 -- Layer 4 (model-specific settings)
    tasks_frontier/           -- 27 frontier tasks (ft-001 through ft-027)
    directives/               -- Domain-specific constraint boxes
    interactive_smoke.py      -- Bidirectional P-pass test script
    tutor_test.py             -- Tutor-style decomposition test
  resources/                  -- This folder — onboarding and recovery
```

## Key Concepts

**P-Pass:** Popperian falsification pass. Generate, attack, fix, repeat until
diminishing returns. The core mechanism.

**HARD/SOFT classification:** Constraints classified as non-negotiable (HARD)
or preference-based (SOFT). Ambiguous defaults to HARD.

**Confer/Defer:** Multi-model protocol. Models review each other's findings
iteratively. Confer = agreement. Defer = escalation to human review.

**Decay curve (D):** Genuine analysis produces diminishing finding rates per
round (the inverse square root law). Chatbot churn produces flat curves.
The shape distinguishes analysis from noise.

**(D, v-bar, A, C) fingerprint:** Four-metric capability assessment.
D = decay rate, v-bar = verification score (SymPy-confirmed fraction),
A = total verified findings, C = coverage of constraint space.

**Constraint Editor (CE):** Hierarchical policy engine. 5 layers cascade
with monotonicity — lower layers cannot weaken higher-layer HARD constraints.

**Domain expert config:** Portable cognitive encoding with three layers:
universal methodology, domain-specific directives, user personalisation.

## Known Confounds (document honestly)

1. **Directive asymmetry:** CC and CX carry the founder's cognitive
   methodology directives (CLAUDE.md) into all conditions. DeepSeek, Gemini,
   and ChatGPT operate with no equivalent. This affects between-model
   comparisons but not between-condition comparisons.

2. **ChatGPT context overflow:** ChatGPT via pipe mode accumulates full
   conversation history. 24 warnings, 1 failure in bench test. Context cap
   not yet applied to ChatGPT (applied to CX only).

3. **SymPy extraction gap:** CC extracts mathematical claims from raw
   findings when models don't include verifiable_claim fields. Extraction
   quality varies — some claims are unparseable by SymPy. The natural
   language mathematical interpretation gap is a known limitation.

4. **Small model population:** 5 frontier models from 4 vendors is the
   available population, not a chosen sample. The diversity hypothesis
   cannot be fully tested until the ecosystem is larger.

5. **HIL prompt narrowing:** The HIL guidance says "focus on these points,"
   which narrows model search. Confirmed by framing bias literature
   (arXiv:2603.18740). Fix designed: iterative 5-round guidance pattern.

6. **ChatGPT hidden system prompt:** ChatGPT 5.4 via proprietary API carries
   a hidden RLHF preamble. Fix designed: OpenRouter access with user-defined
   system prompts.

7. **Phantom HARD inflation:** Default constraint_class was HARD instead of
   SOFT. Fixed in code but affects Run 1 data.

## Communication Protocols

The founder uses single-letter shorthand:
- `y` = yes/approved
- `t` = continue
- `d` = discuss before proceeding
- `p` = run P-pass (falsify)
- `e` = extrapolate beyond immediate domain
- `c` = confer with CX via CLI, run mutual P-passes until convergence
- `a` = analyse dispassionately
- `r` = read IM only (quick context check)
- `rr` = full recovery (re-read all resources, rebuild context from scratch)
- `rs` = external research (web search, arXiv, Semantic Scholar)
- `t` = export to TTS accessibility file
- `sv` = save state (Open Brain + update recovery resources + commit + push)

These compose: `p d e` = falsify, discuss, extrapolate. `c p a d` = confer
with CX, P-pass, analyse, discuss.

## How to Resume Work

1. Read this document
2. Check `git log --oneline -10` for recent commits
3. Check if bench test is running: `ps aux | grep run_round_robin`
4. Read latest log: `tail -30 bench/logs/$(ls -t bench/logs/ | head -1)`
5. Check MEMORY.md for persistent project state (if available)
6. Read FOUNDERS_NOTES.md for design intent and open questions

## How to Reproduce Results

```bash
cd bench
pip install -r requirements.txt
source ../.env    # API keys for DeepSeek, Gemini, OpenAI, Wolfram
python3 run_round_robin.py --phase2 --smoke --tasks ft-001   # single task smoke test
python3 run_round_robin.py --phase2                           # full 26-task bench
```

All results are checkpointed. Use `--resume` to continue after interruption.

## How to Refute Results

Run the bench test yourself. Compare your (D, v-bar, A, C) fingerprints
against the published results. If your Control condition outperforms your
CDSFL+HIL condition, the methodology fails on your tasks. Publish the result.
That is data, not failure.
