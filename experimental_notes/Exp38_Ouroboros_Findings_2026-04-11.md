# Experiment 38 — Ouroboros: Self-Review of Reference Runner

**Date:** 2026-04-11
**Duration:** 8h12m (05:21–14:33 BST, 24 rounds, wall clock cap)
**Termination:** WALL CLOCK CAP (29,503s). Never converged.
**Target Article:** `bench/reference_runner.py`
**Panel:** 5 models — ChatGPT (GPT-5.4/OpenRouter), CC2 (Opus 4.6/claude_cli), Codex (GPT-5.4/OpenRouter), Gemini (3.1 Pro/Google GenAI), DeepSeek (Reasoner/DeepSeek API)
**Topology:** Star (shared findings)
**Pattern:** FFAFP (Find, Follow, Analyse, Fix, P-pass)
**S_k:** Enabled

## Round-by-Round Metrics

| Round | Raw | Novel | Total | rho | rho_avg | gamma | S_k ADM/REJ/ESC | Time (s) |
|-------|-----|-------|-------|-----|---------|-------|------------------|----------|
| R0 (blind) | 25 | 25 | 25 | 1.000 | 1.000 | 0.000 | 4/0/18 | 401.9 |
| R1 | 46 | 36 | 61 | 0.783 | 0.891 | 0.000 | 10/0/21 | 227.5 |
| R2 | 43 | 23 | 84 | 0.535 | 0.772 | 0.000 | 11/0/28 | 255.5 |
| R3 | 20 | 3 | 87 | 0.150 | 0.489 | 0.063 | 10/0/30 | 300.4 |
| R4 | 16 | 0 | 87 | 0.000 | 0.228 | 0.206 | 9/0/30 | 330.9 |
| R5 | 29 | 3 | 90 | 0.103 | 0.084 | 0.301 | 9/0/32 | 328.1 |
| R6 | 17 | 0 | 90 | 0.000 | 0.034 | 0.377 | 4/0/31 | ~300 |
| R7 | 31 | 9 | 99 | 0.290 | 0.131 | 0.417 | 2/0/27 | ~300 |
| R8 | 13 | 0 | 99 | 0.000 | 0.097 | 0.454 | 2/0/27 | ~300 |
| R9 | 32 | 17 | 116 | 0.531 | 0.274 | — | 3/0/28 | ~300 |
| R10 | 31 | 12 | 128 | 0.387 | 0.306 | 0.462 | 6/0/27 | ~300 |
| R11 | 21 | 0 | 128 | 0.000 | 0.306 | 0.465 | 2/0/26 | ~300 |
| R12 | 18 | 7 | 135 | 0.389 | 0.259 | 0.468 | 2/0/32 | 401.7 |
| R13 | 24 | 0 | 135 | 0.000 | 0.130 | 0.474 | 2/0/32 | 221.7 |
| R14 | 31 | 8 | 143 | 0.258 | 0.216 | 0.476 | 1/0/29 | 315.6 |
| R15 | 21 | 0 | 143 | 0.000 | 0.086 | 0.481 | 1/0/30 | 192.3 |
| R16 | 19 | 5 | 148 | 0.263 | 0.174 | 0.485 | 5/0/33 | 316.5 |
| R17 | 16 | 4 | 152 | 0.250 | 0.171 | 0.489 | — | ~300 |
| R18 | 15 | 0 | 152 | 0.000 | 0.171 | 0.493 | — | ~300 |
| R19 | 12 | 7 | 159 | 0.583 | 0.278 | 0.496 | — | ~300 |
| R20 | 17 | 1 | 160 | 0.059 | 0.214 | 0.500 | — | ~300 |
| R21 | 12 | 2 | 162 | 0.167 | 0.270 | 0.503 | — | ~300 |
| R22 | 19 | 1 | 163 | 0.053 | 0.093 | 0.507 | 1/0/37 | 252.1 |
| R23 | 17 | 6 | 169 | 0.353 | 0.191 | 0.510 | 1/0/37 | 274.1 |

**FINAL TOTALS:** 545 raw findings, 169 canonical, 0 S_k rejections, 24 rounds. γ_final=0.510.

## Convergence Signals

- gamma trajectory: 0.000, 0.000, 0.000, 0.063, 0.206, 0.301, 0.377, 0.417, 0.454, 0.462, 0.460, 0.465, 0.468, 0.474, 0.476, 0.482, 0.485, 0.489, 0.493, 0.496, 0.500, 0.503, 0.507, 0.510 — steady rise, crossed "strong depletion" (>0.45) at R8, crossed 0.5 at R20
- rho_avg trajectory: 1.000, 0.891, 0.772, 0.489, 0.228, 0.084, 0.034, 0.131, 0.097, 0.274, 0.306, 0.306, 0.259, 0.130, 0.216, 0.086, 0.174, 0.171, 0.171, 0.278, 0.214, 0.270, 0.093, 0.191 — collapsed then oscillates around 0.10-0.28, mostly in churn
- ITC threshold (0.25) crossed at R4 (rho_avg=0.228), oscillates back above at R9-R12 and R19/R21, mostly below from R13
- Nine zero-novelty rounds (R4, R6, R8, R11, R13, R15, R18, and partial R3/R5/R20/R22) — sawtooth pattern from R7, broke into double-bursts from R16
- **Final HIL flags (59 total):** CC2 21x CAPABILITY_MISMATCH, ChatGPT 13x DEGRADATION, Codex 13x DEGRADATION, DeepSeek 7x DEGRADATION, Gemini 5x
- All 5 models remained active for all 24 rounds (none removed)
- **Convergence gate blockers over experiment:** churn (ρ_avg < 0.25, 14/24 rounds), contested (persistent, 4-12 findings), novel (when burst rounds produced > 0)
- **R21 was closest to convergence** — only blocker was contested=9 (no churn, no novel)
- **Experiment never converged.** Terminated by wall clock cap. Phase 0 consumed entire budget (see bug below)

### Sawtooth Novelty Pattern (R7 onward)

From R7, novelty alternates between burst and zero rounds in a remarkably stable pattern:

| Pattern | Rounds | Amplitudes |
|---------|--------|------------|
| burst | R7, R9, R10, R12, R14, R16, R17, R19, R23 | 9, 17, 12, 7, 8, 5, 4, 7, 6 |
| zero | R8, R11, R13, R15, R18 | 0, 0, 0, 0, 0 |
| near-zero | R20, R22 | 1, 1 |
| low | R21 | 2 |

From R16, strict burst-zero alternation broke down into double-bursts (R16-R17: 5,4) and irregular patterns. Burst amplitude declined through R16-R18 (5 to 4 to 0) then spiked at R19 (7) when models found a new topic vein, before settling to near-zero (R20-R22: 1, 2, 1). Final round R23 produced a 6-novel burst, demonstrating the system can still find novelty even at γ=0.51.

Cause: multi-topic scope. The runner contains convergence logic, ITC, finding lifecycle, burst mode, status transitions, and more. Models cycle through different topic areas, producing novelty bursts when they find a new vein, followed by zero rounds when they revisit already-catalogued issues. In a per-element convergence scheme, individual topics would converge independently and faster.

## Closed Findings (Verified Fixes Applied)

| ID | Closed at | Description |
|----|-----------|-------------|
| C0001 | R3 | — |
| C0026 | R3 | — |
| C0031 | R3 | — |
| C0004 | R6 | Off-by-one in `_compute_rho()` |
| C0005 | R6 | `RunnerConfig.__post_init__` overwrites user-configured `rho_earliest_round` |
| C0029 | R6 | — |
| C0030 | R6 | — |

## Persistently ADMISSIBLE (Surviving S_k Every Round)

C0002, C0032, C0041, C0063, C0085 — all with sk=1.000, S*=0.000, R: 0.500 to 0.367.

## z3-CONFIRMED Findings (B-Cell Grounded Proof)

1. **CC2_F004 (R1):** z3 UNSAT_GROUNDED. Grounded vars: `['total']`.
2. **DeepSeek_F006 (R3):** z3 UNSAT_GROUNDED. Grounded vars: `['total', 'evidence']`. 4 preconditions extracted, Z3 translatable.
3. **ChatGPT_F002 (recurring):** z3 SAT_COUNTEREXAMPLE (REJECTED). Grounded vars: `['rho_earliest_round', 'evidence', 'round_']` and `['round_idx']`.

## Bug: Phase 0 Missing Convergence Overrides

**Severity:** CRITICAL — root cause of the experiment's inability to converge.

Burst mode is active (6 phases + integration, 56-round budget). `phase_convergence_overrides()` in `burst_planner.py` (line 527) returns tighter criteria per phase (`earliest_stop_round: phase_round_offset + 3`, `consecutive_rounds_required: 2`). But these overrides are only applied at phase transitions (`reference_runner.py` line 2831). Phase 0 never gets them — it runs with base config (`earliest_stop_round: 12`).

If overrides were applied at burst initialization, Phase 0 could have converged at round 3 (with the tighter criteria). Instead Phase 0 consumed the entire round budget. Phases 1-5 and integration were never reached.

**Fix:** Apply `phase_convergence_overrides(0)` at burst initialization (line ~2460), not just at transitions.

## Runner Bugs Found by Model Panel (6 Corroborated)

Multi-model corroboration means 2+ independent models reported the same bug in separate rounds. Listed by severity.

| # | Bug | Models | Sev | Rounds |
|---|-----|--------|-----|--------|
| 1 | `_compute_rho()` early return on zero raw findings: aborts instead of computing rolling average | Gemini + DeepSeek | 0.95 | R7+ |
| 2 | `contested_count()` filter: wrong unresolved-challenge logic (checks `status != 'MERGED'` instead of excluding all terminal statuses) | 3x | 0.93 | R3+ |
| 3 | `open_crit_high_count()` missing REOPENED status — reopened findings not counted as open-critical-high | 3x | 0.93 | R3+ |
| 4 | `_compute_rho()` off-by-one: zero-based finding index vs 1-based round counter | 5x | 0.91 | R1+ |
| 5 | `RunnerConfig.__post_init__` silently overrides user-configured `rho_earliest_round` | 2x+ | 0.90 | R2+ |
| 6 | `contested_count()` hardcoded grace period ignores `contested_grace_rounds` parameter | 2x | 0.85 | R5+ |

All 6 are confirmed by multiple independent models and are consistent with observed experiment behaviour. Fixes deferred to Exp 39 (not applied during the live run).

## Design Findings from Experiment Monitoring

### D1: Churn Detection Without Adaptive Response

The convergence gate detects churn accurately (`ρ_avg < 0.25` → `[CHURN]`) but uses it only as a binary gate blocker. There is no feedback loop from churn detection to adaptive action. Three candidate mechanisms:

**A. Burst phase transition trigger.** In burst mode, sustained churn IS the signal that the current phase is exhausted. If the Phase 0 override were in place, tighter `earliest_stop_round: 3` would enable this. Fixing the Phase 0 bug addresses the burst-mode case.

**B. Stall convergence input.** `_check_stall_convergence()` checks `open_ch + contested` stability but not churn duration. If ρ_avg < threshold for N consecutive rounds AND γ > 0.45, that is a stronger stall signal than static count stability.

**C. Dynamic gate relaxation.** When γ > 0.45 (strong depletion, independently confirmed) and churn persists > N rounds, the remaining ρ contributions are re-derivations, not genuine novelty. The gate could relax specific conditions under these jointly-confirmed depletion signals.

### D2: Contested Findings Need Timeout and HIL Escalation

If a finding stays contested for > 2 rounds, models have had multiple opportunities to resolve the disagreement and failed. This is a deadlock, not productive debate. Currently `contested_count()` blocks convergence (requires `contested == 0`) with no timeout or escape.

**Proposed mechanism:**
1. Track per-finding contested duration (rounds since first unresolved challenge).
2. After `contested_escalation_rounds` (default 2), escalate to HIL with finding + all challenge evidence.
3. Remove escalated findings from `contested_count()` — now HIL's responsibility.
4. HIL resolves: CONFIRM, REFUTE, or MERGE.

In Exp 38, 12 contested findings have been blocking convergence for 3+ rounds. With this mechanism, the contested count would have started draining at R14 and the convergence gate would have one fewer blocker.

Both D1 and D2 are detection-without-action gaps: the system measures a condition accurately but does not act on it adaptively. Combined with the Phase 0 override fix, these three changes would substantially improve convergence behaviour in Exp 39.

### D3: z3 Grounding Breakthrough (R22)

The B-Cell produced a z3 SMT-LIB grounded CONFIRMED proof for ChatGPT_F001 in R22, grounding variables `earliest_stop_round` and `rho_earliest_round`. This is the first CONFIRMED finding via formal verification in the later rounds and validates the RunnerConfig `__post_init__` silent override bug (#5 in corroborated bugs). Shows z3 verification works when the claim is about config-space relationships.

### D4: MERGE Deadlock Accumulation

12+ findings persistently MERGE DEFERRED due to target disagreement across all R16-R23 rounds. Same findings appear every round (C0008, C0011, C0015, C0016, C0018, C0037, C0038, C0041, C0044, C0084, C0087, C0090). C0011 has 9 competing merge targets. Models cannot agree on which findings should merge, creating a permanent contested population that blocks convergence. Needs either an automated deduplication heuristic or HIL arbitration.

### D5: Gemini UNSTRUCTURED Finding Format

From R22, Gemini produced at least one finding tagged as `UNSTRUCTURED` — could not be parsed into standard finding format. The parser assigned it to the immune pipeline as-is. Indicates Gemini's output format degrades with accumulated context. Related to P2/P3 parser issues.

### D6: DeepSeek Chunk Delivery Failures

From R18 onward, DeepSeek consistently received non-WAITING responses on chunk 1 delivery (0 chars). The runner retried with chunk 2, and DeepSeek still produced output, but delivery reliability degraded. Codex and DeepSeek both exceeded coherence budgets (density=0.0246 vs budgets 0.012 and 0.01).

## Immune Pipeline Aggregate (Across All 24 Rounds)

- Fix verification outcomes: HARMFUL dominant, UNEVALUABLE dominant for Gemini/DeepSeek
- Gemini: 6/7 findings per round had "Target file not found: None" (known parser bug)
- Reconciliation locks: consistent pattern of ChatGPT and Codex findings being LOCKED as REJECTED
- RT v2 consistently healthy (8-42% removal rate across rounds)
- LLM classifier agreement with regex: 3-25% (typically ~15%). Regex says "mathematical", LLM says "code_behavioral" for runner code findings
- B-Cell: 0 grounded proofs in most rounds; 1 z3 CONFIRMED in R22
- NK increasingly active: 6 bugs closed in R22, 4 in R20

## Parsing and Runner Issues Identified During Monitoring

### P1: S_k ESCALATE — No SEARCH/REPLACE Blocks (159 occurrences)

**Severity:** HIGH — the dominant failure mode throughout the experiment.

Models emit findings without properly formatted SEARCH/REPLACE fix blocks. S_k cannot evaluate fixes without them, resulting in ESCALATE verdict. 159 total escalations across all rounds vs maximum 11 ADMISSIBLE. This means ~75% of all canonical findings are unevaluable by S_k.

**Root cause:** The model prompt does not enforce SEARCH/REPLACE format, or models describe fixes in prose rather than structured blocks. Some models (CC2, DeepSeek, Gemini) consistently fail to produce parseable fix blocks.

**Fix for next runner:** Strengthen the fix-format instructions in the dispatch prompt. Consider providing a concrete SEARCH/REPLACE template. Add a pre-S_k format check that requests reformatting from the model if blocks are missing.

### P2: CC2 Malformed Finding ID — Description Text Leak (6 occurrences, R5-R6)

**Severity:** MEDIUM — wasted processing, garbled log output.

CC2's R5 F003 finding had a DESCRIPTION containing backtick-quoted `"F001"` in analysis prose (discussing alias resolution in the registry). The parser extracted this inner `"F001"` as a separate finding identifier, creating the phantom finding: `CC2_"F001"`, the lookup works. But if the model emits MERGE C0005 <- C0002...`

This garbled ID flowed through the entire immune pipeline (LLM classifier, B-Cell, formalisation agent, fix verification, HIL escalation). The pipeline handled it gracefully (UNEVALUABLE/HIL escalation), but 6 pipeline processing slots were consumed by a phantom.

**Root cause:** The finding parser regex matches quoted identifiers inside DESCRIPTION text rather than only at field-declaration boundaries.

**Fix for next runner:** Tighten the finding parser to match FINDING_ID only at line-start or after a field delimiter. Do not extract identifiers from within DESCRIPTION, PROPOSED_FIX, or FOLLOW text.

### P3: Gemini Verdict-as-Finding-ID (Multiple occurrences, R1-R2)

**Severity:** MEDIUM — same class as P2 but different model.

Gemini's responses mixed verdict declarations (MERGE, CONFIRM, CHALLENGE) with finding declarations. The parser extracted strings like:
- `Gemini_MERGE C0018 <- C0011`
- `Gemini_CONFIRM C0008`
- `Gemini_CHALLENGE C0019`

These were processed as findings and LOCKED as REJECTED by reconciliation (correctly — they are not real findings).

**Root cause:** The parser does not distinguish verdict lines from finding declarations when they share structural markers.

**Fix for next runner:** Parse verdict lines (CONFIRM, MERGE, CHALLENGE) separately and before finding extraction. Strip them from the response before finding parsing runs.

### P4: Fix Verification — Target File Not Found (22 occurrences)

**Severity:** MEDIUM — blocks fix evaluation for a substantial fraction of findings.

CC2 (8), Gemini (3), DeepSeek (6), and others produce PROPOSED_FIX blocks without specifying the target file path. The fix verifier cannot locate the file to apply the patch.

**Root cause:** The PROPOSED_FIX schema does not require a target file field, or models omit it even when instructed.

**Fix for next runner:** Add an explicit `TARGET_FILE` field to the finding schema. Validate its presence before passing to S_k. If missing, attempt to infer from the DESCRIPTION's file reference.

### P5: LLM Classifier "Below Threshold" Log Misleading (Cosmetic)

**Severity:** LOW — cosmetic only.

For MATHEMATICAL findings, the MATHEMATICAL guard prevents LLM override regardless of confidence threshold. But the log message says "below threshold 0.70" which implies the threshold was the deciding factor. In reality, the MATHEMATICAL guard would have blocked the override even at conf=1.0.

**Fix for next runner:** Change the log message from "below threshold X" to "MATHEMATICAL guard retained" when the MATHEMATICAL guard is the active constraint.

### P6: DeepSeek Finding ID Drift (F100)

**Severity:** LOW — cosmetic, no pipeline impact.

DeepSeek emitted `F100` as a finding ID in R6 (normal range is F001-F010). Suggests the model's internal counter has drifted after 7 rounds of interaction. The parser accepted it — the pipeline is ID-agnostic.

**No fix needed.** The parser is correctly flexible on ID format.

## Infrastructure Issues

### Gemini 403 PERMISSION_DENIED (R4 only)

Gemini was blocked by Google Cloud billing enforcement during R4 dispatch. All 5 retry attempts failed. Resolved by the founder paying the outstanding bill — Gemini returned normally in R5 (260.9s response time in R6). No code change was needed.

### google.generativeai Deprecation Warning

Both `google-generativeai 0.8.6` (old) and `google-genai 1.70.0` (new) are installed. The codebase uses the new package, but the old deprecated package fires a FutureWarning from shared namespace. Deferred fix: `pip3 uninstall google-generativeai` (not executed during the live experiment).

## Terminal Summary

Experiment 38 ran 24 rounds (R0-R23) over 8h12m before the wall clock cap terminated it. The experiment never converged. All 24 rounds remained in burst Phase 0 due to the missing convergence override bug — Phases 1-5 and integration were never reached.

**Key metrics:**
- 545 raw findings, 169 canonical entries, 0 S_k rejections
- γ final: 0.510 (strong depletion, crossed 0.5 at R20)
- 59 HIL flags across all 5 models (CC2 worst at 21)
- Closest to convergence: R21 (only blocker was contested=9)
- Contested findings ranged from 4-12 throughout, never reached 0

**What the experiment proved:**
1. The runner contains at least 6 real bugs that multiple models independently found and corroborated
2. γ converges to ~0.5 in Phase 0 — half the initial discovery rate is consumed by round 20
3. Sawtooth novelty is real: models cycle topics, producing burst-zero alternation
4. Contested findings are a convergence killer without timeout/escalation mechanism (D2)
5. The SEARCH/REPLACE parser is the dominant S_k bottleneck (~75% ESCALATE)
6. Regex classifier is fundamentally broken for code findings (~15% agreement with LLM)
7. Gemini's confirmation-finding parser bug generates systematic UNEVALUABLE false negatives

**Exp 39 fix list (ordered by impact):**
1. Phase 0 convergence override bug (CRITICAL — root cause of non-convergence)
2. 6 corroborated runner bugs from model findings
3. D2: Contested timeout and HIL escalation
4. D1: Churn feedback into convergence detection
5. SEARCH/REPLACE parser strengthening (P1)
6. Confirmation-finding parser fix (P2/P3, V-prefix, no target file)
7. D4: MERGE deadlock arbitration
8. Regex classifier replacement or calibration
9. Uninstall deprecated google-generativeai

**Report:** `bench/logs/exp38_ouroboros_20260411T041938Z/exp38_ouroboros_report.json`

## Experiment Scope Assessment

The models examined `bench/reference_runner.py` and found primarily implementation bugs (off-by-one errors, missing status values, parameter handling). Through the runner, they touched:

- **Mathematical model:** rho/gamma computation, ITC thresholds (C0004 off-by-one confirmed)
- **CDSFL scheme elements:** immune pipeline flow, finding registry mechanics, S_k evaluation
- **Integrated schema:** merge/dedup logic, coherence budgets, convergence criteria

However, the review was bottom-up (implementation bugs in one file) rather than top-down (does the architecture work as an integrated whole?). No model systematically reviewed whether the mathematical model's formulas are theoretically correct, or whether the CDSFL scheme's design assumptions hold. That would require separate experiments with different target articles and framing.

## Recommendations

1. Fix P1-P4 parsing issues before Bench Run 2
2. Consider explicit per-element convergence experiments (runner done; mathematical model, immune pipeline, policy engine, composer as separate targets)
3. HIL review of the 5 persistently ADMISSIBLE findings (C0002, C0032, C0041, C0063, C0085)
4. HIL review of z3-CONFIRMED CC2_F004 and DeepSeek_F006
5. Commit the 5 uncommitted fixes in working tree
6. Uninstall the deprecated google-generativeai package
