# CE Benchmark Code Review by CX (Codex) — Rounds 7 and 8

**Date:** 2026-03-18T19:50:00Z

---

## Round 7 Verdict

CX found **2 new HARD defects**. Both implemented by CC.

**1. Corrupt ledger on resume fail-open:** `load_existing()` now returns `bool` and sets `was_corrupt` flag. Resume path refuses to continue if ledger is corrupt with completed checkpoint items.

**2. Duplicate ID type collision:** `validate_frontier_task()` now enforces string type on task IDs. Non-string IDs produce a validation error.

---

## Round 8 Verdict

CX found **1 more edge case** in resume cost-cap logic. CC assessment: this is a false finding.

CX claims prior spend can exist with zero completed checkpoint items because preflight writes ledger without checkpoint entries, and that this creates a fail-open path for the cost cap.

---

## CC Falsification of Round 8 Finding

**Scenario 1 (preflight crash):** Preflight runs, writes to ledger at $0.05, then crashes. On resume: checkpoint has 0 completed items, so abort guards do not fire. Ledger loads with $0.05. Cap enforcement includes the preflight spend. This is correct behavior. No budget overrun occurs.

**Scenario 2 (mid-task crash between `ledger.record` and `checkpoint.record`):** Ledger has cost, checkpoint does not. On resume: task re-runs (correct, since checkpoint does not show completion), and the ledger double-counts the cost. This makes the cap enforcement slightly over-conservative (aborts earlier than needed, not later). Over-conservative is the safe direction. No budget overrun occurs.

**Scenario 3 (corrupt checkpoint):** `was_corrupt` flag is `True`. The code explicitly does NOT load the ledger ("checkpoint was corrupt, ledger also reset to avoid asymmetry"). Both restart from zero. This is correct behavior.

CX's claim that the cap is "under-enforced" does not hold. All edge cases either produce correct behavior or over-conservative cap enforcement. The "fail-open" framing is inaccurate for these scenarios.

**CC's definitive stance:** Diminishing returns have been reached. CX is now finding edge cases that, upon falsification, do not produce the failure they describe.

---

## Cumulative Review Summary (Rounds 1 through 8)

| Metric | Count |
|---|---|
| Total findings across all rounds | 25+ individual defects |
| Genuinely actionable findings implemented | 20+ |
| Known limitations documented | 3 |
| False or already-covered findings | 2–3 |

**Known limitations documented:**
- Task-level cap granularity (not call-level)
- Approximate cost estimator (not billing-grade)
- Manifest scope covers configs, models, passes, and task IDs — but not file content

**The codebase has materially improved across all HARD constraint categories:** checkpoint compatibility, cost-cap enforcement, resume safety, Schema C scoping, assessor parsing, fatal error handling, and data validation.
