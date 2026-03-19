CE Experiment — Locked Design Decisions
========================================

This file is MANDATORY CONTEXT for any reviewer (human or AI) assessing
the benchmark harness. Read before reviewing run_benchmark.py or
run_phase2.py. Decisions here are SETTLED and not subject to re-review
unless the founder explicitly reopens them.

Date: 2026-03-19
Authority: George Jackson (The Founder)


THREE CONDITIONS — ROLES AND RATIONALE
--------------------------------------

  1. CONTROL: Single pass, no system prompt, no iteration.
     PURPOSE: Raw unfiltered model output. The baseline against which
     everything else is measured. Executed FIRST, before any p-passes.
     This is THE control in the scientific sense.

  2. CE (EXPERIMENTAL): Iterative p-passes with CDSFL directives.
     PURPOSE: The experimental condition. Full CE methodology applied.

  3. CALIBRATION BASELINE (PLACEBO): Iterative p-passes with generic
     "be careful, check your work" directives. Same iteration mechanism
     as CE, including adaptive confer termination.
     PURPOSE: Isolates DIRECTIVE CONTENT as the variable. Controls for
     prompt quality and iteration count. If CE beats calibration, the
     specific CDSFL methodology matters. If it doesn't, CE is just
     "think harder" with extra steps.

The calibration baseline DELIBERATELY shares the adaptive confer
mechanism with CE. This is NOT a defect. Without shared iteration
machinery, any CE vs calibration comparison would conflate "better
directives" with "different iteration count."

Three comparisons, three questions:
  Control vs CE          → Does the full methodology beat raw output?
  Calibration vs CE      → Do the specific directives matter?
  Control vs Calibration → Does structured iteration alone help?


NOT DEFECTS (design choices that look like bugs without context)
---------------------------------------------------------------

  - Placebo shares confer mechanism with CE: DELIBERATE. See above.
  - Control is single-pass while CE is iterative: DELIBERATE. The
    control measures raw model capability. Iteration IS part of what
    CE provides.
  - Confer CLI costs are not metered in CostLedger: DELIBERATE. Confer
    uses CC/CX CLI subscriptions (zero API cost), separate from the
    experiment's API budget.
  - Task randomization seed is constant (not manifest-derived):
    DELIBERATE. Same shuffle for all runs ensures consistent task
    ordering across configs and resume. Different task subsets get
    different effective orderings because shuffle operates on
    different lists with the same RNG.
  - Schema C adversarial pass requires max_passes >= 5: BY DESIGN.
    max_passes is the total budget. Warning emitted when Schema C
    runs with fewer.
  - Deferred report only shows RESOLVED/DEFERRED for adaptive
    conditions: CORRECT. Control has no termination decision (single
    pass). Schema C runs to completion. Only adaptive conditions have
    meaningful termination status.


REVIEW HISTORY
--------------

  Rounds  1-8:  CC/CX adversarial review (Anthropic + OpenAI)
  Rounds  9-13: Gemini review (Google, pre-fix code)
  Round  14:    Gemini Extended P-Pass (5 modules, post-fix)
  Round  15:    CC Full P-Pass (4 modular + 1 adversarial, post-fix)
  Total: ~23 review passes across 3 model architectures.

  False positive log:
  - P5 adversarial finding 1 (2026-03-19): "placebo shares confer
    mechanism" flagged as CRITICAL. Reclassified as NOT A DEFECT by
    founder. Root cause: reviewer lacked design context. This file
    created to prevent recurrence.
