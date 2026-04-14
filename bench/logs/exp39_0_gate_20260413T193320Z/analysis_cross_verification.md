# Cross-Verification & Anomaly Analysis — Exp 39-0

## Key Findings Summary

**Two MAJOR parser bugs that need fixing before Exp 39-1. All numerical data cross-checks pass. The decomposition race condition left evidence but the fix is already in place.**

---

## Issue 1: CC2_full_id, — Parser Emitting Source Code as Finding IDs (MAJOR)

**Severity: MAJOR — fix before next run**

The finding ID `CC2_full_id,` (with trailing comma) appears in round_01.json (lines 361, 383), round_04.json (lines 163, 185), and propagates into canonical entry C0023. This is a parser bug — it ingested Python variable names as finding field values:
- `finding_id: "CC2_full_id,"` — the variable name `full_id` from `parse_findings()`
- `description: "description,"` — a keyword argument name from the `Finding()` constructor
- `target_file: "target_file,"` — same pattern
- `proposed_fix` contains literal `findings.append(Finding(...)` source code

Two phantom findings per round, every round R1-R5. Canonicalised as C0023. The immune pipeline correctly marks them DUPLICATE (sim=0.800), limiting damage, but they waste processing and pollute counts.

---

## Issue 2: C0038 — f-string Template Emitted as Finding ID (MAJOR)

**Severity: MAJOR — fix before next run**

C0038 has alias `DeepSeek_f"{model_id}_UNSTRUCTURED",` — a raw Python f-string from the fallback parser code path. Its description is `"response[:500],"` — another code fragment. Same class of bug as Issue 1 but from the fallback/unstructured parser. Phantom canonical entry.

---

## Issue 3: Data Integrity — All Numbers Match (INFO)

Every metric cross-checks between report JSON and relaunch log: 111 total findings, 6 rounds, 41 canonical entries, gamma 0.461, 4388s elapsed. Per-round rho values, registry totals, and finding counts all match within display rounding. Gamma history [0.0, 0.0, 0.4476, 0.4028, 0.4319, 0.4612] is consistent.

---

## Issue 4: DeepSeek R5 at 1125s (MINOR)

DeepSeek timing across rounds: R2=747s, R3=836s, R4=409s, R5=1125s. The R5 outlier is explained by decomposed dispatch where all three phases produced substantial output (10,803 + 11,215 + 16,964 chars). Consistent with DeepSeek-R1's long-reasoning behaviour on complex prompts. DeepSeek R4 is also notable: both section 1 and section 2 returned 0 chars, meaning decomposition provided zero benefit that round. No other model shows anomalous timing.

---

## Issue 5: R2 Decomposition Race Condition Evidence (MAJOR, already fixed)

R2 used decomposed dispatch for ChatGPT, Gemini, and DeepSeek. Evidence of the bug:
- Gemini R2: section 2 returned 0 chars
- DeepSeek R2: section 1 returned 0 chars
- ChatGPT R2: section 2 only 1,996 chars (vs 18,122 for section 1)

R3+ went monolithic for ChatGPT/Gemini/Codex (only DeepSeek stayed decomposed). Finding productivity increased: ChatGPT went from 1 finding in R2 to 5 in R3; DeepSeek from 3 to 6. Quality of individual findings was not degraded — the synthesis phase recovered useful output despite empty sections.

---

## Issue 6: Registry — 41 Entries, 2 Phantom (INFO)

41 canonical entries C0001-C0041 confirmed. next_id=42. Alias map is 1:1 with no double-counting. C0012 correctly merged into C0024. Effective real count: 39 entries (minus C0023 and C0038 from Issues 1-2).

---

## Issue 7: Fingerprints Updated, Minor DeepSeek Gap (INFO/MINOR)

All 5 fingerprints updated at experiment end time. Values sensible. DeepSeek's `prompt_chars_history` has only 3 entries vs 6 for all other models — missing R0/R1 data, possibly due to relaunch initialisation. Does not affect operation but could bias fingerprint-based dispatch.

---

## Issue 8: Output Sizes — Normal Depletion Pattern (INFO)

Response sizes (chars) per model per round:

| Round | CC2 | ChatGPT | Codex | DeepSeek | Gemini |
|-------|------|---------|-------|----------|--------|
| R0 | 12,712 | 24,431 | 18,725 | 20,209 | 11,306 |
| R1 | 16,607 | 19,424 | 22,272 | 22,703 | 14,605 |
| R2 | 17,398 | 13,623 | 14,166 | 10,750 | 16,094 |
| R3 | 16,885 | 14,404 | 11,847 | 12,642 | 17,671 |
| R4 | 18,464 | 8,071 | 21,686 | 8,178 | 4,777 |
| R5 | 8,231 | 13,065 | 12,689 | 16,964 | 8,362 |

Gemini R4 (4,777) is the experiment minimum. Codex R4 (21,686) is an outlier high — it found new material while others depleted. DeepSeek R5 (16,964) doubled its R4 output, correlating with the 1125s timing. General trend is declining output toward R4-R5, consistent with convergence. No outputs below 4,000 (dispatch failure) or above 30,000 (hallucination).
