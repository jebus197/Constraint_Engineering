# CE Benchmark Code Review by CX (Codex) — Round 3

**Date:** 2026-03-18T19:21:47Z
**Context:** Review of all 7 Round 2 remediations plus full P-pass of updated code

---

## Round 3 Verdict

Not at diminishing returns yet: **3 substantive HARD defects remain** (Schema C prevalidation scoping vs tasks, Schema C manifest compatibility gap, and hard cost-cap enforcement gap).

---

## Constraint Classification

- **HARD:** checkpoint compatibility correctness, cost-cap enforcement, task/config selection safety, schema gating correctness
- **SOFT:** logging clarity, type annotations/docstring fidelity, estimator precision

---

## Round 2 Fix Verification (7 items)

1. **Schema C pre-validation scoping:** Partially fixed (pair scoping works, but still over-scoped vs selected tasks).
2. **Schema C runtime guard continue bug:** Fixed (`skip_pair` correctly skips whole pair).
3. **Empty task selection crash:** Fixed (explicit `if not tasks: sys.exit(1)`).
4. **Manifest under-spec:** Partially fixed (task IDs added, missing-manifest warning added; Schema C dependencies still omitted).
5. **DEFERRED_INFRA logic:** Fixed (ANY infra failure now triggers at hard cap).
6. **Pass-count validation:** Fixed (`choices=range(3,6)`).
7. **Preflight metering:** Fixed for metering, not fixed for cap enforcement.

---

## Remaining Substantive Defects

**1. Schema C env validation still over-scoped to non-Schema-C task selections.**
Logic always adds Schema C pair env keys when pair models exist in `configs` plus `CX_CONFIGS`, independent of whether selected tasks include any `schema_c` task (`bench/run_phase2.py` lines 651, 653, 655). Runtime only runs Schema C if `schema_c_tasks` exists (lines 789, 790).
*Reproduction (static):* selected tasks `ft-001`, `ft-003`, `ft-005` yielded `schema_c_tasks_count` of 0 but prevalidation still required `ANTHROPIC_API_KEY`.

**2. Manifest remains under-specified for Schema C resume compatibility.**
Manifest hashes only selected configs passed from main loop, not `CX_CONFIGS` used by Schema C (`bench/run_phase2.py` lines 137, 672, 795). Schema C checkpoint key uses pair name, not model/provider fingerprint (line 526).
*Reproduction (static):* mutating `CX_CONFIGS` `sonnet-4-thinking` model left manifest unchanged, so incompatible Schema C checkpoints can be accepted on resume.

**3. Hard cost cap is not enforced before API calls in two paths.**
`run_preflight()` meters calls but never checks cap before control or CE call (`bench/run_phase2.py` lines 390, 402, 416). `run_task_conditions()` checks cap only after control call (lines 453, 467).
*Reproduction (mocked):* with `cap_usd` of `0.0`, preflight still executed both calls; with cap already reached, `run_task_conditions` still executed one control call.

**4. (SOFT) Cross-file contract drift in confer API typing and docs.**
Annotated as returning 2-tuple (`bench/run_benchmark.py` line 1019). Actually returns 3-tuple at all exits (line 1198). Caller expects 3-tuple (line 1289). Runtime works internally, but this is a maintenance and static-analysis hazard.

---

## CC Proposed Fixes for Round 4

- **Fix 1** (Schema C env over-scoped vs tasks): Only add Schema C pair env keys to the validation set when the selected tasks actually contain at least one task with `schema_c` set to `True`.
- **Fix 2** (Manifest for Schema C): Include `CX_CONFIGS` in the manifest hash when Schema C is active (not skipped and `schema_c` tasks exist).
- **Fix 3** (Pre-call cost cap check): Add `ledger.check_cap()` guard before every API call in `run_preflight()` and at the top of `run_task_conditions()`.
- **Fix 4** (Confer return type annotation): Update the function signature annotation to match the actual 3-tuple return.
