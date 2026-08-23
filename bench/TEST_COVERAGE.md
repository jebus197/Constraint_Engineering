# Bench Test Coverage

253 tests across 26 test classes. All in `bench/tests/test_dynamic_management.py`.

Last updated: 30 March 2026.

---

## Area 1: Configuration and Data Structures (14 tests)

**TestDynamicManagementConfig** (9 tests). Validates the central configuration object: default values, role assignment weight vectors (alpha) sum to 1, non-negative, 4-dimensional, max rounds positive, tau_kappa in range, feasibility threshold in range, correct alpha and baseline vector retrieval per role.

**TestCapabilityFingerprint** (3 tests). Conversion to numpy array, normalisation inverts decay rate (lower decay = higher capability), zero-max edge case.

**TestModelSpec** (2 tests). Default latency standard deviation is zero. Class is frozen (immutable).

---

## Area 2: Role Assignment (15 tests)

**TestRoleAssignment** (15 tests). Single model → PM. Two models → PM + Participant. Three models → all roles. PM locked. Capability scores computed correctly. Ordering sorted descending. Failure history recorded. Failure rate zero with no history. Reassignment applies failure penalty. Hysteresis prevents role oscillation. Reassignment with subset of active models. Edge cases: k=1, homogeneous models.

---

## Area 3: Load Balancing (16 tests) — SHELVED 2026-08-22

Area 3 is SHELVED as of 2026-08-22 (founder ruling: shelve, do not retire). The 16 tests below still run and still pass, and that is the whole point of the entry: they are the only place `bench/dm/_load_balancer.py` has ever executed. Passing tests here are not evidence that the component is commissioned. See `bench/dm/_load_balancer.py` for the three grounds, and `bench/tests/test_load_balancer_shelved.py` for the check that keeps the runner off it.

**TestLoadBalancer** (13 tests). Solve returns valid allocation. Every task covered. PM excluded when k>1. k=1 PM handles all. High criticality → full redundancy. Empty tasks. Feasibility probability: deterministic, uncertain, well-below-mean. Dispatch blocks when uncertain, passes when within capacity. Edge cases: k=1, homogeneous.

**TestAllocation** (3 tests). Get assigned models, get assigned tasks, model load computation.

---

## Area 4: Round Progression (19 tests)

**TestRoundProgressionFSM** (19 tests). Initial state BLIND. BLIND → SYNTH → ROUND_1. Progression to max. CONVERGED terminates. DIMINISHED terminates. FAIL_CRITICAL terminates from any state. Terminal rejects transitions. Invalid events rejected. Valid events accepted. History recorded. Event selection priority. CONVERGED > DIMINISHED. MAX at final round. Raises when nothing applicable. Edge cases: k=1, no failures, linear chain.

---

## Area 5: Convergence Detection (18 tests)

**TestConvergenceDetector** (13 tests). Three-metric convergence: kappa_set (no novelty, with novelty), kappa_rate (basic, round zero), kappa_adopt. Combined = min. Requires min rounds. Severity veto blocks convergence. Realistic sequence. Single-linkage equivalence classes. Gamma estimation. Edge cases: k=1, no findings.

**TestFindingSimilarity** (5 tests). Same class no description. Different class same description. Different class different description. Same class identical description. Same class partial overlap.

---

## Area 6: Diminishing Returns Detection (18 tests)

**TestDiminishingReturnsDetector** (14 tests). Marginal value: basic, first round, zero cost, zero cost+delta, missing round. Smoothed marginal value. Stop: not before r_min, when diminished. Ascending abstraction guard conjunctive. Abstraction dropping detected. Add round from findings. Remaining value via Duane. Edge cases: k=1, homogeneous.

**TestPerModelMu** (4 tests). Basic per-model mu. Attrition-resistant. Aggregate uses max. Fallback to system mu.

---

## Area 7: Failure Handling (38 tests)

**TestFailureHandler** (25 tests). No failure on valid response. Empty/whitespace/timeout/malformed/format violation detection. Underperformance requires persistence window. Priority: empty > timeout. Recovery: retry first, exclude on repeat, extended timeout, clarified prompt, degraded mode, log only, downgrade. PM failure → retry then abort. Exclude removes from active. Abort below k_min. Abort when PM not active. Cascade reallocation guard. Failure history tracked. Event callback fires. Edge cases: k=1, no failures.

**TestCorrelatedFailureModel** (13 tests). Default vulnerability zero. Self-vulnerability one. Set/get vulnerability. Range validation. Base rate validation. Pairwise joint: independent, correlated, bounded. Class failure: single model, empty set, increases with vulnerability. Independence check (partial and full).

---

## Area 8: Immune Layer and Health Monitoring (57 tests)

**TestDetectorHealthMonitorExp15** (12 tests). Vocab growth tracking. Model failure detection: 1 failure (no trigger), 2 consecutive (WARNING), 3 consecutive (CRITICAL). Reset on success. Findings decline detection with noise filtering. Vocab saturation detection. Remediation state tracking. Outcome verification: success and failure. Remediation log accumulation.

**TestRemediationChains** (10 tests). Kappa chain step 0, escalation, exhaustion. Findings decline → deferred (human-in-the-loop). Deferred approval/rejection. Model failure → pre-decompose. Damping prevents oscillation. Vocab saturation halves threshold. Immune disabled skips all.

**TestSelfAdaptiveImmuneLayer** (23 tests). Level 3 self-monitoring: outcome tracking, default success rate, natural resolution, chain exhaustion, step effectiveness, recommended chain start (default, skip ineffective, keep working). P-pass: no contraindications, rejects failed, skips improving, warns mixed. Self-diagnosis: low success rate, bounded windows, high false positives, chain exhaustion. Summary. Adjustment log persists. Verification feeds tracker. Natural resolution on kappa resolve. Chain skip in apply_diagnosis. P-pass rejection escalates. Wired into record_round.

**TestExtendedPPassImmune** (12 tests). Single-module → standard P-pass. Multi-module → extended. Cascade risk. Over-specification. Simplification suggestion. Clean pass. Self-adjustment: approves coherent, rejects contradictory, warns cumulative risk. Iterates to simplest. Defers when all rejected. Worst-performer identification.

---

## Area 9: Experiment 15 Detectors (19 tests)

**TestParserYieldDetector** (6 tests). No trigger: normal response, small response, failed model. Triggers on large response + zero parsed findings (format divergence). Escalates WARNING → CRITICAL. Independent per model.

**TestMonotonicDeclineDetector** (7 tests). No trigger: insufficient data, non-monotonic, small decline. Triggers on 3-round monotonic decline ≥ 3. Escalates on persistence. Resolves on recovery. Independent per model.

**TestCostPerFindingSpikeDetector** (6 tests). No trigger: insufficient data, stable CPF, zero findings. Triggers when CPF > mean + 2σ. No trigger on moderate variation. Independent per model.

---

## Area 10: Integration and Edge Cases (24 tests)

**TestDynamicManager** (13 tests). Initial state. Roles assigned. Allocation produced. Round advances FSM. Full run to terminal. Critical failure terminates. Dispatch feasibility: deterministic, uncertain blocks, uncertain warns. Event stream populated. Correlated failures accessible. Round results accumulate. Role reassignment after round.

**TestReductionProperties** (2 tests). All mathematical reduction properties hold with default config and custom config.

**TestEdgeCases** (9 tests). Single model full workflow. Event priority enum. Finding equivalence class properties and empty case. Failure type ordering. Round state format. Allocation at zero limit. Custom similarity function. No active models raises.

---

## Other (8 tests)

**TestVocabSaturation** (6 tests). Growth first round. Decreases. New terms. Sustained window required. Triggers stop. Not triggered with fresh content.

**TestWindowedFingerprint** (2 tests). Does not collapse (unlike EMA). Falls back to EMA when window is zero.

---

## Summary by Management Area

| Area | What it tests | Tests |
|------|--------------|-------|
| 1. Configuration | Defaults, validation, weight vectors | 14 |
| 2. Role Assignment | PM/COL/PAR assignment, failure penalty, hysteresis | 15 |
| 3. Load Balancing | Task allocation, feasibility, dispatch | 16 |
| 4. Round Progression | FSM states, transitions, termination | 19 |
| 5. Convergence | Kappa metrics, equivalence classes, severity veto | 18 |
| 6. Diminishing Returns | Marginal value, Duane extrapolation, per-model mu | 18 |
| 7. Failure Handling | Typed failures, recovery, correlated failures | 38 |
| 8. Immune Layer | Health monitoring, remediation, self-adaptive, extended P-pass | 57 |
| 9. Exp15 Detectors | Parser yield, monotonic decline, cost-per-finding | 19 |
| 10. Integration | Full workflow, reduction properties, edge cases | 24 |
| Other | Vocab saturation, windowed fingerprint, event stream | 15 |
| **Total** | | **253** |
