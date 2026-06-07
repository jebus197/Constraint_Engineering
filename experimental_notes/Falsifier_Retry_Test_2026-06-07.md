# Falsifier Error-Correction Retry Test + Verdict-Correctness Audit

**2026-06-07 10:29 BST.** Tests whether feeding the Exp-42 residuals' errors back to their source models resolves them — and, critically, whether the resolutions are *correct*. Source: the 15 un-falsifiable criticals from `bench/logs/exp42_composer_20260606T202037Z`.

## 1. Setup

- **Harness hardening (applied, `bench/falsifier_verify.py::_sandbox_env`):** put both repo root AND `bench/` on PYTHONPATH so a falsifier resolves `from bench.cdsfl_registry.X import` OR `from cdsfl_registry.X import`; neutralises the relative `sys.path.insert(0,'bench')` class that broke in the throwaway CWD. Gate-on only (reverify runs only under the gate).
- **Retry:** each residual's finding + broken falsifier + the runner's re-run error fed back to its **source model**, ONE shot, asking for a corrected runnable falsifier. The **runner** (`reverify_falsifier`) re-runs the fix and decides — no verdict dictated to the model. ("Real deal, don't rig it.")

## 2. Resolution — 10/15 (harness + single retry)

Final verdicts: **7 CONFIRMED, 3 REFUTED, 5 ERROR.** Path: **4 resolved by harness alone** (the relative-`sys.path` class), **6 by retry**, 5 unresolved (need the max-3 cap). Source split of residuals: 10 DeepSeek, 4 Gemini, 1 ChatGPT.

| id | src | resolved via | final | id | src | resolved via | final |
|---|---|---|---|---|---|---|---|
| C0028 | DeepSeek | harness | REFUTED | C0019 | DeepSeek | retry | REFUTED |
| C0029 | DeepSeek | harness | CONFIRMED | C0023 | Gemini | retry | CONFIRMED |
| C0032 | DeepSeek | harness | CONFIRMED | C0031 | Gemini | retry | CONFIRMED |
| C0033 | DeepSeek | harness | CONFIRMED | C0037 | DeepSeek | retry | CONFIRMED |
| | | | | C0040 | ChatGPT | retry | REFUTED |
| | | | | C0046 | Gemini | retry | CONFIRMED |

Still ERROR (→ would continue to retry 2–3, else HIL): C0015, C0034, C0036, C0054, C0063 (4 DeepSeek, 1 Gemini).

**Conclusion:** the retry idea is validated — given the actual error, a model usually fixes its own broken test. Genuine incapability is rare on a coding task.

## 3. Verdict-correctness audit (10-agent Workflow `wf_b62f363c`, each verifying against the real source)

**8/10 correct. The 2 errors are entirely one-sided — both false REFUTED.**

| runner verdict | correct | note |
|---|---|---|
| **CONFIRMED** | **7/7** | all real defects, demonstrated for the right reason (C0023, C0046 "partial" test but correct verdict) |
| **REFUTED** | **1/3** | C0019 genuine non-defect (correct); **C0028, C0040 FALSE — real defects masked** |

**The 2 false REFUTED (sy-verified):**
- **C0028** (sev 0.95): compose (composer.py:1361–1363) applies `_apply_phenotype_transform` to the HARD situation packet with no `constraint_class` guard (vs the HARD-protected domain loop 1346–1349); the four_layer packet is corrupted (1880→1836 chars, 26→11 lines). The falsifier compares `sit_pkt.text != situation.text` but compose **mutates `situation.text` in place** (1362), so the comparison is trivially equal → clean exit → false REFUTED. My corrected falsifier (snapshot `str(situation.text)` before compose) shows `changed=True` and `situation.text == final` is `True` — defect real, verdict wrong.
- **C0040**: `_load_universal_directive` (composer.py:591–595) sets `use_minimal` via `len(full_text) > max_directive_chars` regardless of `format_style`; the full universal text (19,696 chars) exceeds every model cap, so `_load_universal_directive("opus_4_6")` returns the 2,503-char minimal render even though opus_4_6 is the `format_style="full"` model — exactly the claimed silent replacement. The retry falsifier built inert cloned `PhenotypeTransform` objects and introspected a loader whose signature accepts only a `model` string, so it never exercised the shipped caps → clean exit → false REFUTED.

**The asymmetry has a clean mechanistic cause:** CONFIRMED requires the falsifier to *actively demonstrate* the defect (raise AssertionError / print FALSIFIED) — hard to fake. REFUTED is a *passive clean exit* — a broken test that does nothing in particular also clean-exits. So **CONFIRMED is trustworthy by construction; REFUTED is only as trustworthy as the test's setup.**

## 4. Convergence analysis (round data, `exp42_composer_report.json`)

- `novel_this_round`: **15 → 8 → 6 → 5 → 4 → 4 → 5 → 1 → 4 → 3 → 1** — panel approaching quiescence (down to 1 new by R11).
- `unverified_critical` (A4 blocker): **0 → 1 → 2 → 3 → 5 → 9 → 12 → 13 → 7** — the **dominant** blocker; A4 explicitly prevents the zero-critical streak from accruing while these pend.
- `gamma_critical`: hovered ~0.49–0.57 (≠ ~1.0 clean convergence).

**Honest verdict:** resolving the residuals **can** take Exp 42 over the line — the panel was nearly quiet and A4 (the residuals) was the primary blocker; the runner clears A4 *genuinely* (it re-runs each fix and decides — the flag is not faked). **BUT** a naive retry leaves 2 false REFUTED → Exp 42 would declare success while silently carrying 2 real defects labelled non-defects. **Not a rigged flag — a correct flag on wrong data**, which is worse for looking clean.

## 5. The fix the evidence demands

1. **Harness hardening** — applied (free win).
2. **Retry, max-3, → HIL escape** — validated; build into the gate (re-dispatch source model with the runner's error on ERROR/missing falsifier).
3. **Refutation scrutiny (the load-bearing addition)** — trust CONFIRMED as-is (7/7); accept a REFUTED only if the falsifier *actually set up and exercised the claimed condition*. Both false REFUTED fail this (C0028 compared a mutated-in-place value; C0040 used an inert clone). Mechanism: a REFUTED on an independently-likely-real finding → re-ask the model to prove its test triggers the claimed precondition, else → HIL. **Not model voting — a structural check on the identified REFUTED weakness.**
4. **Severity calibration** — still warranted (9/15 over-rated, prior note) to reduce the new-critical rate.

**Definitive convergence test = implement (2)+(3)+(4) in the runner + re-run Exp 42.** A naive re-run would converge dishonestly; the refutation-scrutiny is what makes a re-run "the real deal."

## 6. Commits

Harness hardening in `bench/falsifier_verify.py` (this note's commit). Prior session: `fbafff8` falsifier mechanism, `1169f2b` B-Cell, `5e81c94` S_k, `e976dcb`/`6c09c26` tracker + Exp 42 record.

---
*Written under CDSFL note standard v1.2 (14 May 2026). Plain-English: `Falsifier_Retry_Test_Plain_English_2026-06-07.md`; TTS: `~/Desktop/CDSFL_tts/Falsifier_Retry_Test_and_Confirm_Refute_Asymmetry_2026-06-07.txt`.*
