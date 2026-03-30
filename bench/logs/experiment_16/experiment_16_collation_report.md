# Experiment 16 Collation Report

**Date:** 30 March 2026
**Collator:** CC1 (Opus 4.6)
**Test article:** Experiment 17 plan (bench/logs/experiment_17_plan.md)
**Models:** CC2, Codex, ChatGPT, Gemini, DeepSeek — all 5 succeeded

## Response Summary

| Model | Chars | Time (s) | Findings | Open Q | Improvements |
|-------|-------|----------|----------|--------|-------------|
| CC2 | 23,955 | 145.7 | 12 (PF001-PF012) | 4 | 8 (IMP001-IMP008) |
| Codex | 7,904 | 380.4 | 8 (PF001-PF008) | 4 | 7 (IMP001-IMP007) |
| ChatGPT | 19,702 | 87.9 | 24 (PF001-PF024) | 4 | 20 (IMP001-IMP020) |
| Gemini | 6,332 | 38.5 | 4 (PF001-PF004) | 4 | 3 (IMP001-IMP003) |
| DeepSeek | 9,713 | 167.4 | 6 (PF001-PF006) | 4 | 7 (IMP001-IMP007) |
| **Total** | **67,606** | **819.9** | **54** | **20** | **45** |

## Convergent Themes (3+ models independently agree)

### Theme 1: Blind round contradicts providing findings (4/5)
**Models:** CC2 PF002, Codex PF003, ChatGPT PF005, Gemini Q2
**Resolution:** Split Round 0 into R0A (blind discovery) + R0B (seeded validation).
**Dissent:** DeepSeek Q2 — provide for calibration baseline. Overruled by majority.

### Theme 2: Self-orchestration circularity (3/5)
**Models:** CC2 PF003 (0.85), ChatGPT PF007 (0.91), Codex PF006 (0.76)
**Resolution:** Add independent stop caps (round 10, wall-clock 4h). Mandatory round-level
telemetry for external audit. Full shadow controller deferred (disproportionate for scope).

### Theme 3: Code extract scope insufficient (5/5)
**Models:** CC2 PF001, Codex PF001/PF002, ChatGPT PF002, Gemini PF001, DeepSeek PF002
**Resolution:** Provide full `dynamic_management.py` with analytical boundary in prompt.
Add dependency interface summary. This was the strongest convergence (all 5 models).

### Theme 4: Success criteria weak/circular (4/5)
**Models:** CC2 PF006, Codex PF005, ChatGPT PF015/PF016/PF017, Gemini PF002
**Resolution:** Reframed as behaviour validation. "Immune actions are justified" replaces
"3 models survive." Abstraction guard validated via scenario + natural firing.

### Theme 5: Cross-model agreement not verification (3/5)
**Models:** CC2 PF010, Codex PF007, ChatGPT PF010
**Resolution:** Downgraded to corroborative evidence. Require independent artifact.

### Theme 6: SymPy partially applicable (3/5)
**Models:** CC2 PF007, ChatGPT PF011, Gemini PF004
**Resolution:** SymPy verification required for mathematical operations in immune code.

### Theme 7: Fix ordering dependency-aware (3/5)
**Models:** CC2 PF008, ChatGPT PF012, Gemini PF003
**Resolution:** Build fix DAG before applying. Prerequisites before dependents.

### Theme 8: Missing telemetry (3/5)
**Models:** ChatGPT PF021 (0.88), DeepSeek IMP004, CC2 IMP001
**Resolution:** Mandatory round-level logging of all immune decisions.

### Theme 9: Need fault injection (4/5)
**Models:** CC2 IMP005, Gemini IMP002, ChatGPT IMP007, DeepSeek IMP003
**Resolution:** Added induced-failure scenarios (canary, false positive, cascade, oscillation).

### Theme 10: DeepSeek decomposition (5/5)
**Resolution:** Decompose into 3 sub-areas. Unanimous.

### Theme 11: Load balancing separate with interface (5/5)
**Resolution:** Test separately, include interface contracts. Unanimous.

## Open Question Consensus

| Question | CC2 | Codex | ChatGPT | Gemini | DeepSeek | Resolution |
|----------|-----|-------|---------|--------|----------|------------|
| Q1 Decomposition | Yes (3 areas) | Yes (policy) | Yes | Don't fragment | Yes (3 areas) | Decompose for DeepSeek |
| Q2 Blind findings | No (blind first) | No (blind first) | No (0A+0B) | No (hidden rubric) | Yes (provide) | Split R0A/R0B |
| Q3 Damping rounds | 2 | 2 | 1 | 1 | 3 | 2 (median, instrumented) |
| Q4 Load balancing | Separate+interface | Separate+probes | Separate+interaction | Separate+mock | Separate+interface | Separate+interface |

## Notable Non-Convergent Findings

- **ChatGPT PF023 (0.81):** Single experiment pass insufficient; need baseline + induced-failure + stress runs. Noted but not adopted — disproportionate for current scope.
- **Gemini IMP001:** Model version strings flagged as hallucinated. False alarm — versions are current. [VERIFY:current] flag appropriate given training cutoff.
- **ChatGPT IMP001:** Full shadow/external controller. Deferred — telemetry + independent caps are the simplest sufficient mitigation.
- **DeepSeek Q3:** immune_damping_rounds = 3. Outlier. 3 would delay immune actions past useful window in short experiment.

## Severity Distribution (top findings by severity)

| Severity | Finding | Model | Theme |
|----------|---------|-------|-------|
| 0.99 | PF001 scope truncated | Codex | Theme 3 |
| 0.97 | PF002 scope truncated | Codex | Theme 3 |
| 0.95 | PF001 extraction breaks | Gemini | Theme 3 |
| 0.91 | PF007 self-orchestration | ChatGPT | Theme 2 |
| 0.90 | PF004 dispatch policy | Codex | Theme 3 |
| 0.88 | PF003 blind contradiction | Codex | Theme 1 |
| 0.88 | PF021 missing telemetry | ChatGPT | Theme 8 |
| 0.86 | PF013 weak regression gate | ChatGPT | Theme 7 |
| 0.85 | PF003 circular stop | CC2 | Theme 2 |
| 0.85 | PF002 survival criterion | Gemini | Theme 4 |
