# CDSFL Methodology Self-Test — Ground Truth Defects

**Target:** run_benchmark.py at commit 61228c8 (805 lines, 2 providers)
**Compiled:** 2026-03-19 01:21 UTC
**Sources:** CX review (8 rounds), Gemini review (5 rounds), CC p-pass

---

## Code Defects

*Findable by reviewing run_benchmark.py alone.*

### GT-01: Draft Pollution Fallback

- **Location:** `run_experimental` line 390, `run_extended` line 458
- **Defect:** `current_draft = extracted_revision or response`. When model omits `REVISED_ANSWER` section, entire raw response (including `ISSUES_FOUND` metadata, labels, self-criticism) becomes the "draft" for the next pass. This causes recursive context pollution where the model critiques its own metadata instead of the actual answer.
- **Severity:** HIGH
- **Found by:** Gemini R1 (#3), R2 (#6), R3 (#2), R4 (#4)

### GT-02: Gemini Safety Filter Crash Path

- **Location:** `call_gemini` is NOT present at 61228c8 (only anthropic and openai providers exist)
- **Status:** NOT APPLICABLE at this baseline. Gemini provider was added later.

### GT-03: Extended Mode Off-By-One

- **Location:** `run_extended` line 404–410
- **Defect:** `modular_count = max(num_passes - 1, 1)`. With `--passes 1`, runs 1 modular pass PLUS 1 adversarial pass = 2 total, violating the user's constraint. No CLI validation prevents this.
- **Severity:** MEDIUM
- **Found by:** Gemini R1 (#9), R2 (#9)

### GT-04: Case-Sensitive Section Extraction

- **Location:** `_extract_section` lines 276–291
- **Defect:** Label matching is strictly case-sensitive (`REVISED_ANSWER` only). Models frequently output `"Revised Answer:"`, `"revised_answer:"`, etc. When extraction fails due to case mismatch, triggers GT-01 (draft pollution).
- **Severity:** HIGH
- **Found by:** Gemini R2 (#6)

### GT-05: Format Injection via `.format()`

- **Location:** `_build_pass_prompt` lines 302, 308 (`INITIAL_PASS_TEMPLATE.format()`, `FOLLOWUP_PASS_TEMPLATE.format()`)
- **Defect:** Python `.format()` crashes with `KeyError` or `ValueError` when task prompts or model-generated drafts contain curly braces (e.g., mathematical set notation `{x, y, z}`). A single such task kills the entire benchmark run.
- **Severity:** HIGH
- **Found by:** Gemini R3 (#3)

### GT-06: Recursive Label Truncation in `_extract_section`

- **Location:** `_extract_section` lines 276–291
- **Defect:** Stop-pattern lookahead will prematurely truncate extraction if a model's `REVISED_ANSWER` contains one of the section labels in prose (e.g., "This fixes the issue found in `INITIAL_ANSWER`"). Silent data loss — only the text before the embedded label is recorded.
- **Severity:** MEDIUM
- **Found by:** Gemini R4 (#2)

### GT-07: Stop-Pattern Section Leakage

- **Location:** `_extract_section` lines 276–291
- **Defect:** Stop pattern requires newline before next label. If model puts content on the same line as the NEXT label (e.g., `"ISSUES_FOUND: None"`), the lookahead fails and extraction continues past the section boundary, consuming the next section's content.
- **Severity:** MEDIUM
- **Found by:** Gemini EPP M1 (#1)

### GT-08: Extended Mode Does Not Match Documented 4+1 Method

- **Location:** `run_extended` lines 404–490
- **Defect:** Implementation runs standard iterative full-task passes for `1..(n-1)`, then isolates only the final pass. No module-scoped decomposition, no module map. Default pass count is 3, not the documented 4+1. Results from `--mode extended` cannot evidence the formal Extended P-Pass hypothesis.
- **Severity:** HIGH (scientific validity)
- **Found by:** CX C3

### GT-09: Only 2 Providers in `PROVIDERS` Dict

- **Location:** `PROVIDERS` dict line 262
- **Defect:** Only `"anthropic"` and `"openai"` registered. No Gemini, Groq, Codex, or reasoning-model support. Phase 2 configs reference providers that don't exist.
- **Severity:** HIGH (blocks Phase 2 execution)
- **Found by:** Gemini R1 (#2)

### GT-10: No Retry/Backoff for Transient API Errors

- **Location:** `run_experimental`, `run_extended` (call sites)
- **Defect:** API calls are made directly with no retry logic. A single 429, 503, or timeout crashes the run. No exponential backoff.
- **Severity:** MEDIUM
- **Found by:** Gemini R1 (#4)

### GT-11: History Deletion Confound in Extended Mode

- **Location:** `run_extended` adversarial pass (line 462)
- **Defect:** The adversarial pass deletes issue history (only receives draft + original task). Performance improvement in extended mode conflates "fresh context" benefit with "noise removal" benefit. Scientifically uninterpretable.
- **Severity:** MEDIUM (scientific validity / design-level)
- **Found by:** Gemini R3 (#1)

---

## Design-Level Concerns

*Findable but not code bugs.*

### GT-D1: No Cost Tracking or Budget Enforcement

The baseline has no `CostLedger`, no cost estimation, no budget cap. Unbounded API spend.

### GT-D2: No Checkpoint/Resume Capability

No crash recovery. Interrupted runs must restart from scratch.

### GT-D3: No Calibration/Placebo Baseline Condition

Only control and experimental. No way to isolate methodology from prompt quality.

---

**Total:** 10 code defects (GT-01 through GT-11, excluding GT-02 which doesn't apply) plus 3 design-level concerns.
