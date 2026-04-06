# CX + Gemini Runner 36 Review Results

**Date:** 7 April 2026, 00:05 BST
**Reviewed by:** CX (GPT-5.4 via OpenRouter) + Gemini (3.1 Pro via Google API)
**Target:** `bench/run_exp36_evidence.py`
**Method:** Sequential CDSFL FFF review (CX then Gemini), focused on new CC2v, stall detector, and gate softening components

---

## Summary

| Metric | Value |
|--------|-------|
| Total unique findings | 12 |
| TRUE (genuine bugs) | 9 |
| PARTIAL (valid concern, overstated) | 3 |
| FALSE (code is correct) | 0 |
| Genuine finding rate | 100% (all identified real issues) |
| Fixes applied | 5 must-fix, both runners |

**vs Pre-Exp 35 review:** 9% genuine rate (1/11) -> 100% genuine rate (12/12). Dramatically better signal. Likely because (a) the review prompt was more focused and specific, and (b) the new components had real integration bugs.

---

## Findings Triage

### Confirmed and Fixed (Must-Fix)

| # | Finding | Reviewers | Severity | Fix |
|---|---------|-----------|----------|-----|
| CX2/6/7/8 | Checkpoint ordering: runner_state.json written BEFORE gate_history, open_ch_history, stall_history mutated by convergence checks. Resume loses one round of history. | CX | LOGIC_ERROR | Moved checkpoint write after convergence/stall checks |
| G1 | ESCALATE verdicts silently dropped: default confidence 0.5 < threshold 0.7, ESCALATE handler dead code | Gemini | LOGIC_ERROR | ESCALATE exempted from confidence gating |
| G2 | ESCALATE re-selection loop: escalated findings stay OPEN, re-selected into CC2v batch every round | Gemini | LOGIC_ERROR | `cc2v_escalated` flag, excluded from batch selection |
| CX3 | CC2v calls `mark_verified()` on CONFIRM, corrupting "fix verified" semantics. Single CC2v pass makes findings unchallengeable. | CX | LOGIC_ERROR | Removed `mark_verified()` from CC2v CONFIRM path |
| G3 | REFUTED findings invisible in `build_summary()`. Falls through both active and resolved sections. Models rediscover and re-file. | Gemini | DATA_FLOW | Added REFUTED to resolved section |

### Confirmed, Not Fixed (Should-Fix / Minor)

| # | Finding | Reviewers | Severity | Status |
|---|---------|-----------|----------|--------|
| CX5 | Docstring says "CRIT/HIGH" but code selects all severities | CX | DOC_MISMATCH | Fixed (docstring updated) |
| G4 | `response_chars` used as `max_successful_context_chars` — stores output length as input capacity | Gemini | LOGIC_ERROR | Deferred — consequence overstated, truncation preserves artifact |
| CX4 | CC2v effects not processed by `_update_finding_statuses` in same round | CX | LOGIC_ERROR | Accepted — one-round delay on CLOSED transition, not fundamental |
| CX1 | `round_data["stall_detector"]` added after dict appended to results | CX | MINOR | Accepted — functionally harmless (dict reference) |

---

## Per-Reviewer Performance

| Reviewer | Findings | TRUE | PARTIAL | FALSE | Hit Rate |
|----------|----------|------|---------|-------|----------|
| CX | 8 | 7 | 1 | 0 | 100% |
| Gemini | 4 | 3 | 1 | 0 | 100% |

Both reviewers produced exclusively real findings. CX found more issues (8 vs 4) but 4 of its 8 were the same root cause (checkpoint ordering). Gemini found fewer but higher-impact issues (ESCALATE dead code, re-selection loop, REFUTED invisibility).

---

## Fix Verification

All 5 fixes applied to both runners (exp35 + exp36). 690 tests pass.

Changes per fix:
1. **Checkpoint ordering:** moved `runner_state.json` write after `_check_state_convergence()` and `_check_stall_convergence()` calls
2. **ESCALATE bypass:** moved ESCALATE handling before confidence gate with `continue`
3. **ESCALATE re-selection:** added `cc2v_escalated` flag to entry, filtered in batch selection
4. **mark_verified removal:** CC2v CONFIRM now calls `registry.resolve()` only
5. **REFUTED in build_summary:** added `refuted` list, included in resolved section header and display
