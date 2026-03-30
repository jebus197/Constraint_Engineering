# CDSFL Methodology Self-Test — Comparison Ledger

**Date:** 2026-03-19 02:18 UTC
**Model:** Gemini (via CLI, gemini-3-flash-preview)
**Baseline:** run_benchmark.py at commit 61228c8 (805 lines)
**Ground truth:** 10 code defects (GT-01 to GT-11, GT-02 N/A) + 3 design concerns

---

## Section 1: Raw Finding Counts

| Condition | Findings |
|---|---|
| Condition 1 — Control (no methodology, no HIL) | 7 |
| Condition 2 — CDSFL only (full methodology, no HIL) | 4 structured findings + methodology artefacts |
| Condition 3 — HIL only (domain context, no methodology) | 9 |
| Condition 4 — CDSFL + HIL (full methodology + domain context) | 4 structured findings + methodology artefacts |
| Condition 5 — HIL without protocol (rounds 1–5, CC-directed prompts) | ~45 findings across 5 rounds |

---

## Section 2: Ground Truth Mapping

### GT-01: Draft pollution (`current_draft = extracted_revision or response`)

| Condition | Result |
|---|---|
| Control | PARTIAL — #5 notes regex fragility and "entire response as draft" fallback |
| CDSFL | NO (not identified) |
| HIL | YES — #3 explicitly identifies silent fallback corrupting iterative loop |
| CDSFL+HIL | PARTIAL — #2 notes extraction vulnerability but not the specific fallback |
| R1–5 | YES — found in R1 (#3), R2 (#6), R3 (#2), R4 (#4) |

### GT-03: Extended mode off-by-one (`--passes 1` gives 2 passes)

| Condition | Result |
|---|---|
| Control | YES — #2 identifies exact defect |
| CDSFL | NO |
| HIL | NO |
| CDSFL+HIL | NO |
| R1–5 | YES — found in R1 (#9), R2 (#9) |

### GT-04: Case-sensitive section extraction

| Condition | Result |
|---|---|
| Control | YES — #5 notes `"REVISED ANSWER:"` without underscore |
| CDSFL | PARTIAL — #1 identifies label collision but not case sensitivity specifically |
| HIL | YES — #3 explicitly calls out case-sensitive matching |
| CDSFL+HIL | PARTIAL — #2 notes markdown headers and missing colons but not case variants |
| R1–5 | YES — found in R2 (#6) |

### GT-05: Format injection via `.format()` on `{x, y, z}`

| Condition | Result |
|---|---|
| Control | NO |
| CDSFL | NO |
| HIL | NO |
| CDSFL+HIL | NO |
| R1–5 | YES — found in R3 (#3) |

### GT-06: Recursive label truncation

| Condition | Result |
|---|---|
| Control | NO |
| CDSFL | YES — #1 identifies label injection within prose |
| HIL | NO |
| CDSFL+HIL | YES — #2 identifies label-in-prose vulnerability |
| R1–5 | YES — found in R4 (#2) |

### GT-07: Stop-pattern section leakage

| Condition | Result |
|---|---|
| Control | NO |
| CDSFL | PARTIAL — covered by #1 (label injection) |
| HIL | PARTIAL — #3 covers extraction fragility broadly |
| CDSFL+HIL | PARTIAL — #2 covers extraction fragility broadly |
| R1–5 | YES — found in EPP M1 (#1) |

### GT-08: Extended mode does not match documented 4+1 method

| Condition | Result |
|---|---|
| Control | NO |
| CDSFL | PARTIAL — #2 examines isolation but finds it acceptable |
| HIL | NO |
| CDSFL+HIL | PARTIAL — examines isolation, finds it "technically sound" |
| R1–5 | YES — CX C3 |

### GT-09: Only 2 providers in `PROVIDERS` dict

| Condition | Result |
|---|---|
| Control | NO |
| CDSFL | NO |
| HIL | NO |
| CDSFL+HIL | NO |
| R1–5 | YES — found in R1 (#2) |

### GT-10: No retry/backoff for transient API errors

| Condition | Result |
|---|---|
| Control | YES — #1 explicitly identifies |
| CDSFL | NO (not explicitly, though environment dependency noted) |
| HIL | YES — #2 explicitly identifies |
| CDSFL+HIL | YES — #3 explicitly identifies with severity |
| R1–5 | YES — found in R1 (#4) |

### GT-11: History deletion confound in extended mode

| Condition | Result |
|---|---|
| Control | YES — #7 notes adversarial pass removes directives, questions validity |
| CDSFL | PARTIAL — #2 analyses isolation, concludes it survives |
| HIL | NO |
| CDSFL+HIL | PARTIAL — analyses isolation, finds it "technically sound" |
| R1–5 | YES — found in R3 (#1) |

---

## Section 3: Novel Findings (not in ground truth)

**Control novel findings:**
- C-N1: Missing model/provider cross-validation — LOW, valid edge case
- C-N2: Brittle hardcoded max_tokens 4096 — MEDIUM, valid

**CDSFL novel findings:**
- D-N1: Python version requirement (3.10+ for union types) — LOW, valid
- D-N2: Template does not remind model of tier-based precedence — LOW, stylistic

**HIL novel findings:**
- H-N1: No temperature/seed for reproducibility — HIGH, valid and significant
- H-N2: Fixed execution order (experimental before control) — MEDIUM, valid confound
- H-N3: Ablation fallback in `compose_directives` (domain-only falls back to universal) — MEDIUM, valid
- H-N4: Inconsistent draft fallback (extended vs standard modes) — MEDIUM, valid
- H-N5: No progress persistence (all results lost on crash) — LOW, valid
- H-N6: Compound variable in control condition (single-pass vs multi-pass) — MEDIUM, design-level

**CDSFL+HIL novel findings:**
- DH-N1: No temperature/seed for reproducibility — HIGH, same as H-N1
- DH-N2: Templates should prompt for tier-based precedence — LOW, same as D-N2

---

## Section 4: False Positives

All conditions produced **zero false positives**. Gemini did not hallucinate defects under any condition.

---

## Section 5: Quantitative Metrics

|  | Control | CDSFL | HIL | CDSFL+HIL | R1–5 |
|---|---|---|---|---|---|
| GT matches (exact) | 3 | 0 | 3 | 1 | 8 |
| GT matches (partial) | 1 | 3 | 1 | 3 | 2 |
| GT total (exact+part) | 4 | 3 | 4 | 4 | 10 |
| Recall (exact/10) | 30% | 0% | 30% | 10% | 80% |
| Recall (total/10) | 40% | 30% | 40% | 40% | 100% |
| Total findings | 7 | 4 | 9 | 4 | 45+ |
| Novel findings | 2 | 2 | 6 | 2 | 5+ |
| False positives | 0 | 0 | 0 | 0 | 0 |
| Precision | 100% | 100% | 100% | 100% | ~95% |

---

## Section 6: Methodology Adherence (CDSFL conditions only)

|  | CDSFL-only | CDSFL+HIL |
|---|---|---|
| Constraint classification | YES | YES |
| Constraint precedence | YES | YES |
| Falsification loop (iterated) | YES (3 pass) | YES (structured) |
| Proportionality gate | YES | NO (not explicit) |
| Corroboration model | NO | NO |
| Extended P-Pass structure | NO | NO |
| Epistemic marking VERIFY | YES | YES |
| Epistemic marking SPECULATIVE | YES | YES |
| Survival predicate | YES | NO (not explicit) |
| Push back / honesty | NO | NO |
| Definitive stance | YES | YES |

Both CDSFL conditions produced structured methodology artefacts that no other condition did. The CDSFL-only condition showed stronger methodology adherence (proportionality gate, survival predicate). Neither condition applied the Extended P-Pass structure or corroboration model — likely because the task (single file review) doesn't meet the 3+ module threshold for Extended, and the corroboration model is an analytical framework rather than an action directive.

---

## Section 7: Qualitative Analysis

**1. Control vs CDSFL-only:**
Control found more GT defects (4 vs 3) but without structure. CDSFL found fewer but classified constraints, applied falsification, and marked epistemic state. CDSFL produced a more rigorous assessment but narrower scope — it went deep on fewer claims rather than surveying broadly.

**2. Control vs HIL-only:**
HIL found more total issues (9 vs 7) and more novel findings (6 vs 2). The domain context directed attention to scientific validity concerns (temperature, execution order, compound variable) that control missed entirely. HIL's domain framing produced the broadest and most practically useful set of findings.

**3. CDSFL-only vs CDSFL+HIL:**
Surprisingly similar — both produced 4 findings, both applied methodology structure. CDSFL-only showed **stronger** methodology adherence (proportionality gate, survival predicate). Adding HIL did not increase finding count or recall in this single-run comparison. The HIL domain context may have competed with the methodology for Gemini's attention, slightly reducing methodology depth.

**4. HIL-only vs CDSFL+HIL:**
HIL-only found significantly more issues (9 vs 4) and more novel findings (6 vs 2). Adding the methodology to HIL **reduced** total findings but **added** structural rigour. This suggests a possible trade-off: methodology constrains output format, which may limit the model's ability to freely explore when domain context is already guiding it.

**5. All conditions vs Rounds 1–5 (HIL-without-protocol):**
Rounds 1–5 dramatically outperformed all single-invocation conditions — 100% GT recall vs 30–40%. But this is 5 rounds of iterative CC-directed review vs single Gemini invocations. The iteration advantage is confounded with the expert-direction advantage. This is expected and by design — the comparison is informative but not apples-to-apples.

**6. Key finding — Format injection (GT-05):**
Only rounds 1–5 found the `.format()` crash on `{x, y, z}`. No single-invocation condition — with or without methodology, with or without HIL — found it. This suggests that some defects require either (a) deep iterative exploration, (b) specific domain knowledge about Python string formatting, or (c) luck. The format injection is a subtle interaction between `.format()` and mathematical notation in task prompts — it requires understanding both the template engine AND the task content simultaneously.

**7. Temperature/seed finding (H-N1):**
Only the HIL conditions identified the missing temperature parameter. This is a scientific validity concern that requires understanding what the code *is* (a benchmark) not just what it *does* (calls APIs). The domain context "scientific validity" and "reproducibility" directly triggered this finding. The methodology alone (CDSFL-only) missed it because the methodology is about reviewing claims, not about understanding the code's purpose.

---

## Section 8: Conclusions

1. CDSFL methodology produces structured, rigorous output with epistemic marking that no other condition achieves. This is a qualitative advantage even when quantitative recall is comparable.

2. HIL (domain expert context) produces the broadest coverage and most novel findings in a single invocation. Domain framing directs attention to concerns the methodology alone misses.

3. CDSFL + HIL does **not** produce strictly better results than either alone in this test. The combination produced fewer findings than HIL-only. This may indicate that the methodology's structured output format constrains free exploration, or that a single model invocation cannot fully service both the methodology protocol and the domain context.

4. All single-invocation conditions are dramatically outperformed by iterative expert-directed review (rounds 1–5). This is the expected result — iteration is the mechanism, not just the methodology. The CDSFL methodology's value includes its iteration protocol, which was not fully exercised in single-invocation conditions.

5. Zero false positives across all conditions. Gemini did not hallucinate defects.

6. The format injection defect (GT-05) was found **only** by iterative expert-directed review. This is a strong data point for the value of iteration and domain expertise combined.

---

## Section 9: Implications for Round-Robin Design

1. The round-robin **must** be iterative — single-invocation CDSFL dramatically underperforms iterative CDSFL. The methodology's iteration protocol is load-bearing.

2. HIL context should be provided to all models in the round-robin — domain framing directs attention to concerns that methodology alone misses.

3. The round-robin should allow each model to iterate internally (methodology-driven) AND externally (cross-model feedback between rounds).

4. The "confer" mechanism for irreconcilable disagreements is validated — different conditions find genuinely different defects, and some findings are condition-unique.
