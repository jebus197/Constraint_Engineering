# Experiment 38 — Ouroboros: Self-Review of Reference Runner

**Date:** 2026-04-11
**Duration:** ~5h (04:19–09:25 UTC+1, R0–R6 completed, R6 immune pipeline in progress at pause)
**Target Article:** `bench/reference_runner.py`
**Panel:** 5 models — ChatGPT (GPT-5.4/OpenRouter), CC2 (Opus/claude_cli), Codex (GPT-5.4/OpenRouter), Gemini (3.1 Pro/Google GenAI), DeepSeek (Reasoner/DeepSeek API)
**Topology:** Star (shared findings)
**Pattern:** FFF
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
| R6 | 17 | 0 | 90 | 0.000 | 0.034 | TBD | TBD | — |

Totals: 196 raw findings, 90 canonical, 0 S_k rejections across all rounds.

## Convergence Signals

- gamma trajectory: 0.000, 0.000, 0.000, 0.063, 0.206, 0.301 — steady rise, "moderate depletion, consistent with PoC convergence"
- rho_avg trajectory: 1.000, 0.891, 0.772, 0.489, 0.228, 0.084, 0.034 — clear monotonic convergence
- ITC threshold (0.25) crossed at R4 (rho_avg=0.228)
- Two zero-novelty rounds (R4, R6) — panel fully recycling
- Three models flagged for consecutive DEGRADATION: ChatGPT (5), CC2 (5), Codex (3)
- All 5 models remain active (none removed)

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

## Immune Pipeline Aggregate (Across Rounds)

- Fix verification outcomes: 37 HARMFUL, 57 UNEVALUABLE, 22 "Target file not found"
- HIL escalations per round: R0(15), R1(varies), R2(varies), R3(varies), R4(1), R5(10), R6(TBD)
- Reconciliation locks: consistent pattern of ChatGPT and Codex findings being LOCKED as REJECTED
- RT v2 consistently healthy (20-25% removal rate)

## Parsing and Runner Issues Identified During Monitoring

### P1: S_k ESCALATE — No SEARCH/REPLACE Blocks (159 occurrences)

**Severity:** HIGH — dominant failure mode throughout experiment.

Models emit findings without properly formatted SEARCH/REPLACE fix blocks. S_k cannot evaluate fixes without them, resulting in ESCALATE verdict. 159 total escalations across all rounds vs maximum 11 ADMISSIBLE. This means ~75% of all canonical findings are unevaluable by S_k.

**Root cause:** Model prompt does not enforce SEARCH/REPLACE format, or models describe fixes in prose rather than structured blocks. Some models (CC2, DeepSeek, Gemini) consistently fail to produce parseable fix blocks.

**Fix for next runner:** Strengthen the fix-format instructions in the dispatch prompt. Consider providing a concrete SEARCH/REPLACE template. Add a pre-S_k format check that requests reformatting from the model if blocks are missing.

### P2: CC2 Malformed Finding ID — Description Text Leak (6 occurrences, R5-R6)

**Severity:** MEDIUM — wasted processing, garbled log output.

CC2's R5 F003 finding had a DESCRIPTION containing backtick-quoted `"F001"` in analysis prose (discussing alias resolution in the registry). The parser extracted this inner `"F001"` as a separate finding identifier, creating the phantom finding: `CC2_"F001"`, the lookup works. But if the model emits MERGE C0005 <- C0002...`

This garbled ID flowed through the entire immune pipeline (LLM classifier, B-Cell, formalisation agent, fix verification, HIL escalation). Pipeline handled it gracefully (UNEVALUABLE/HIL escalation), but 6 pipeline processing slots were consumed by a phantom.

**Root cause:** Finding parser regex matches quoted identifiers inside DESCRIPTION text rather than only at field-declaration boundaries.

**Fix for next runner:** Tighten the finding parser to match FINDING_ID only at line-start or after a field delimiter. Do not extract identifiers from within DESCRIPTION, PROPOSED_FIX, or FOLLOW text.

### P3: Gemini Verdict-as-Finding-ID (Multiple occurrences, R1-R2)

**Severity:** MEDIUM — same class as P2 but different model.

Gemini's responses mixed verdict declarations (MERGE, CONFIRM, CHALLENGE) with finding declarations. The parser extracted strings like:
- `Gemini_MERGE C0018 <- C0011`
- `Gemini_CONFIRM C0008`
- `Gemini_CHALLENGE C0019`

These were processed as findings and LOCKED as REJECTED by reconciliation (correctly — they're not real findings).

**Root cause:** Parser doesn't distinguish verdict lines from finding declarations when they share structural markers.

**Fix for next runner:** Parse verdict lines (CONFIRM, MERGE, CHALLENGE) separately and before finding extraction. Strip them from the response before finding parsing runs.

### P4: Fix Verification — Target File Not Found (22 occurrences)

**Severity:** MEDIUM — blocks fix evaluation for a substantial fraction of findings.

CC2 (8), Gemini (3), DeepSeek (6), and others produce PROPOSED_FIX blocks without specifying the target file path. The fix verifier cannot locate the file to apply the patch.

**Root cause:** PROPOSED_FIX schema doesn't require a target file field, or models omit it even when instructed.

**Fix for next runner:** Add explicit `TARGET_FILE` field to the finding schema. Validate its presence before passing to S_k. If missing, attempt to infer from the DESCRIPTION's file reference.

### P5: LLM Classifier "Below Threshold" Log Misleading (Cosmetic)

**Severity:** LOW — cosmetic only.

For MATHEMATICAL findings, the MATHEMATICAL guard prevents LLM override regardless of confidence threshold. But the log message says "below threshold 0.70" which implies the threshold was the deciding factor. In reality, the MATHEMATICAL guard would have blocked the override even at conf=1.0.

**Fix for next runner:** Change log message from "below threshold X" to "MATHEMATICAL guard retained" when the MATHEMATICAL guard is the active constraint.

### P6: DeepSeek Finding ID Drift (F100)

**Severity:** LOW — cosmetic, no pipeline impact.

DeepSeek emitted `F100` as a finding ID in R6 (normal range is F001-F010). Suggests model's internal counter has drifted after 7 rounds of interaction. Parser accepted it — the pipeline is ID-agnostic.

**No fix needed.** Parser is correctly flexible on ID format.

## Infrastructure Issues

### Gemini 403 PERMISSION_DENIED (R4 only)

Gemini was blocked by Google Cloud billing enforcement during R4 dispatch. All 5 retry attempts failed. Resolved by user paying the outstanding bill — Gemini returned normally in R5 (260.9s response time in R6). No code change was needed.

### google.generativeai Deprecation Warning

Both `google-generativeai 0.8.6` (old) and `google-genai 1.70.0` (new) are installed. The codebase uses the new package, but the old deprecated package fires a FutureWarning from shared namespace. Deferred fix: `pip3 uninstall google-generativeai` (not executed during live experiment).

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
6. Uninstall deprecated google-generativeai package
