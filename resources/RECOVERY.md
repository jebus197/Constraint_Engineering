# Recovery Protocol

Last updated: 12 April 2026 21:33 BST

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
## Current Pending Work (12 April 2026 21:31 BST)

784 tests pass (+22 new). Branch: `exp39-experimental`. Last commit: 89b6a05.

**ALL 9 IMPLEMENTATION PHASES COMPLETE (Phases 0–8):**
- 11 commits on `exp39-experimental` (ad53693..89b6a05)
- New modules: `bench/dm/_similarity.py`, `bench/dm/_memory.py`, `bench/ouroboros_cell.py`
- Mathematical appendix expanded: 1334 → 1651 lines, 7 new sections, 17 notation entries
- 3 critical errors caught/corrected: corroboration collapse, order dependence, kappa overflow

**Gemini Confer Findings (3 rounds, 12 April 2026):**

Round 1 (O1 + FFAFP): advisory capacity falsified as mitigation. Confer: `bench/logs/confer_o1_ffafp/`
Round 2 (PE 3-Gate + O1 Calibration): sensitivity dial, dual-fuse breaker, two-tier clustering. Confer: `bench/logs/confer_pe_o1_design/`
Round 3 (Gap Analysis + Domain-Agnostic Redesign, Codex timed out):
- **Code-correctness bias identified**: all gates, docs, confers framed around code artifacts. CDSFL is domain-agnostic.
- **Gates redesigned**: G1=Mechanical Validity, G2=Semantic Delta, G3=Adversarial Consistency. `IFalsificationGate` protocol interface. Domain configs supply concrete checks.
- **Missing domain configs**: biology, information_science, immune/engineering, cs_software — BLOCKING Exp 39-G/H/M/F.
- **O1 must NOT have external research**: monitor, not actor. External research → ResearchB_Cell.
- **§7 partitioned**: §7.1a churn (BLOCKING), §7.5 sycophancy (LOAD-BEARING), §7.7 severity fusion (LOAD-BEARING). Rest → Phase 9.
- **Convergence gate insufficient**: current γ+ρ cannot distinguish refinement from oscillation without churn (C6).
- Confer: `bench/logs/confer_gap_analysis/`

**Priority ordering (Gemini):**
BLOCKING: domain-agnostic gate interface, convergence churn (C6), missing domain configs
LOAD-BEARING: specialist B-Cell dispatch, sycophancy detection, severity fusion
ENHANCEMENT: Ising/Boltzmann Branch 2, O1 external research (ResearchB_Cell)
PHASE 9: §7.2-7.4, §7.6 (Abstraction Index, Cognitive Yield, Value Estimator, Adoption Delta)

**Agreed execution order:**
1. Domain-agnostic gate interface (IFalsificationGate protocol + GateResult)
2. Convergence gate: add churn detection (§7.1a) as C6
3. Missing domain configs (biology, info science, engineering immune, cs_software)
4. B-Cell dispatch: route to domain-specific tools from new TOML configs
5. Severity fusion (§7.7) for gate output synthesis
6. Sycophancy detection (§7.5) — can shadow alongside 39-0
7. O1 calibration: sensitivity dial, circuit breaker, semantic clustering
8. Run 39-0 (infrastructure gate), then 39-A
9. MC command sync across all reference locations
10. Phase 9 (research write-up) — deferred post-Exp 39

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
