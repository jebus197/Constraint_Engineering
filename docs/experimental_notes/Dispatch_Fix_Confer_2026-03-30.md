# Dispatch Decomposition Fix — Confer Record

Date: 2026-03-30
Participants: CC1 (collator), CC2 (player_manager), CX (independent falsifier)

## Problem
Codex timing out on 112K immune prompts. Decomposition logic had bugs:
(1) feasibility gate skipped decomposed models, (2) no sub-area escalation,
(3) detector key mismatch in _report_dispatch_failure, (4) no throughput model.

## Round 1 Results

### CC2: 7 findings (structured CDSFL format)
- CC2_F001 (0.85): Oscillation risk if throughput data from sub-area dispatches
  is used for task-level feasibility. Proposed tagging throughput observations.
- CC2_F002 (0.90): Mathmodel + appendix = 110K, not 54K. Two tasks need
  sub-area handling, not one. CRITICAL — changed the design.
- CC2_F003 (0.70): Separate context-window vs throughput gates.
- CC2_F004 (0.55): Use median-of-3 for throughput, not running average.
- CC2_F005 (0.80): No re-check after auto-decomposition. Same root cause as crash.
- CC2_F006 (0.45): Throughput tracking belongs in runner, not LoadBalancer.
- CC2_F007 (0.60): Cache key doesn't include decomposition level.

### CX: 0 structured findings, extensive empirical data
- Confirmed actual prompt sizes via code execution
- Found detector key mismatch: "dispatch_watchdog" doesn't match any branch
  in apply_diagnosis(). Immune remediation for dispatch failures was silently
  failing. CRITICAL — would have been a silent bug in production.
- Confirmed immune layer diagnosed CC2 and Codex model_failure in Round 1

## CC1 P-Pass on Round 1

### Validated:
- CC2_F001: Oscillation real but deferred (pre_decompose_models is add-only)
- CC2_F002: CRITICAL. Corrected sizes, added mathmodel sub-areas
- CC2_F004: Median-of-3 implemented
- CC2_F005: Sub-area escalation implemented
- CC2_F006: Throughput in runner layer, passed to check_dispatch_feasibility

### Challenged:
- CC2_F003: Separate gates premature for 5-10 observations. Single min() + metadata.

### Deferred:
- CC2_F007: Cache key change risks HARD constraint. Advisory only.
- CC2_F001 tagging: Document invariant, don't build infrastructure.

### CX empirical finding (detector key): CRITICAL fix applied immediately.

## Converged Changes (implemented)

1. Fixed detector key: "dispatch_watchdog" → "model_failure" (matches apply_diagnosis)
2. Added TASK_SUBAREAS with mathmodel sub-areas (Config, Convergence, DiminishingReturns)
3. Added SUBAREA_ESCALATION_CHARS = 80K threshold
4. _build_decomposed_prompt now escalates to sub-area when task-level > threshold
5. Removed `not decomposed` guard from feasibility gate
6. Added in-memory throughput tracking (median-of-3)
7. Throughput-derived effective_capacity passed as max_chars to decomposition
8. Throughput check fires even when context-window check passes

## Result
- immune: 112K → sub-area rotation (12-93K per sub-area)
- mathmodel: 110K → sub-area rotation (15-34K per sub-area)
- loadbalancing: 42K (unchanged, below threshold)
- persistence: 27K (unchanged, separate file)
- 350 tests passing, Exp 20 (formerly Exp 18) imports verified
