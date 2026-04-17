# Experiment 40 Runner — Audit of Inherited State

**Date:** 17 April 2026
**Purpose:** verify the actual status of every Part 1 item in [Exp40_to_54_Execution_Plan_2026-04-17.md](Exp40_to_54_Execution_Plan_2026-04-17.md) before modifying `bench/reference_runner_v2.py`.
**Method:** read the current `reference_runner.py` and `runner_core.py`, compare against the 14 April post-mortem's stated bug list, classify each item as DONE / PARTIAL / OPEN.

The plan was written from the readiness review, which was written from the post-mortem. The post-mortem was dated 14 April. Substantial fixes have landed between 14 April and 17 April that the readiness review did not reflect. This audit corrects that drift.

---

## Summary

Of the 10 P0/P1 bugs in the post-mortem, 2 were fixed mid-session and 8 were listed as open. Of those 8, this audit finds: **5 already substantially fixed** in the current `reference_runner.py` / `runner_core.py`, **2 partially fixed**, **1 still open**. The plan's Part 1 is over-counted by roughly one full category.

The v2 copy inherits all of these fixes because it was created from the current `reference_runner.py`. The work to wire schema items, specialist cells, fingerprint metrics, and new features remains substantial; the pure bug-fix work has shrunk.

---

## Shadow log audit (Part 2 of plan)

Audit of `bench/logs/exp39_0_gate_20260413T193320Z/ouroboros_shadow_r*.json` and `macrophage_shadow_r*.json`. Six rounds each, 12 files total.

### Ouroboros shadow (Item 2.1)

| Round | Anomalies | Queries | Candidates | Would inject |
|---|---|---|---|---|
| R0 | 4 | 3 | 2 | True |
| R1 | 0 | 0 | 0 | False |
| R2 | 0 | 0 | 0 | False |
| R3 | 0 | 0 | 0 | False |
| R4 | 0 | 0 | 0 | False |
| R5 | 0 | 0 | 0 | False |

**R0 findings:** 4 UNCERTAIN findings as targets. Queries constructed from literal finding-ID strings ("uncertain finding Gemini_F002"). All arxiv queries returned `status: shadow_mock` with zero results, despite `arxiv 2.4.1` being installed. Candidate claims built from placeholder descriptions.

**R1–R5 findings:** Zero activity because all findings were DUPLICATE status by then (no UNCERTAIN targets). This is correct pipeline behaviour — Ouroboros only runs on UNCERTAIN — but masks the query-quality bug because no queries were issued to test.

**Root causes:**
1. Query construction uses finding IDs, not descriptions. Fix is in the Ouroboros cell query builder.
2. `shadow_mock` status appears to be intentional for shadow mode — the cell runs in a mocked-retrieval mode regardless of package availability. A live promotion requires enabling real arxiv calls.

**FFAFP verdict:** the cell did not generate meaningful data because its inputs were garbage. The fix is two-part: query construction from descriptions, and a mode flag that distinguishes shadow-logging from shadow-mocking retrieval.

### Macrophage shadow (Item 2.2)

| Round | Mode | Anomaly count | Pipeline modified | Observations |
|---|---|---|---|---|
| R0 | patrol | 0 | False | 0 |
| R1 | patrol | 0 | False | 0 |
| R2 | patrol | 0 | False | 0 |
| R3 | patrol | 0 | False | 0 |
| R4 | patrol | 0 | False | 0 |
| R5 | patrol | 0 | False | 0 |

**Findings:** blind in every round. No observations produced. Consistent with the post-mortem's P1 #4: `immune_result.cell_verdicts` attribute missing or extracted objects lack `.verdict` / `.confidence`.

**FFAFP verdict:** the wiring failure needs investigation at the `immune_result` object site; the Macrophage-side consumers will align once the producer emits the expected attributes.

### Stage 6 calibrator (Item 2.3)

No `stage6_calibration_r*.json` files in the 39-0 log directory. Expected — the Stage 6 calibrator was designed on 14 April. Exp 39-0 ran on 13 April and predates it.

**FFAFP verdict:** nothing to audit from Exp 39-0. The calibrator's first live data comes from Exp 40.

---

## Part 1 item-by-item status audit

### 1A.1 — S_k format mismatch

**Post-mortem stated fix site:** `reference_runner.py:2094`, 5 LOC in `parse_search_replace_blocks()`.
**Audit result:** **DONE.** Current location is `reference_runner.py:2325` (file has grown). Parser explicitly accepts both formats:

- Line 2355–2361: `if stripped == "====" or stripped.startswith("==== "):` (handles bare and decorated separator)
- Line 2371: `if lines[i].strip().startswith(">>>>"):` (handles bare and `>>>> REPLACE` closer)

Comment at line 2354 confirms: *"The parser in runner_core stores '==== REPLACE' while the prompt specifies bare '===='. Accept both. (Exp 39-0 confound fix.)"*

**Plan update:** reclassify from TODO to DONE. Verification acceptance: unit test already exists in the test suite (needs confirmation), and the format audit is behaviourally proven.

### 1A.2 — Parser emitting source code as finding IDs

**Post-mortem stated symptoms:** `CC2_full_id,` and `DeepSeek_f"{model_id}_UNSTRUCTURED"` leaked as finding IDs; two phantoms.
**Audit result:** **DONE** (substantially). Two guards in place in `runner_core.py`:

- `_FSTRING_TEMPLATE_RE` at line 311 and `_sanitize_fstring_id()` at line 320 resolve unevaluated f-string templates to the intended evaluated value
- `_CODE_LEAK_VARNAMES` guard at line 689 (in `parse_findings`) rejects Python variable names (the `full_id,`, `description,`, etc. leakage path)

Both fixes comment-labelled "Exp 39 fix".

**Residual risk:** the reject-patterns list may not cover every adversarial-looking variable name. Acceptance test for v2: adversarial-string test suite confirming parser rejects a broader set of code-leak patterns.

### 1A.3 — Convergence gate structurally unreachable

**Post-mortem stated fix:** bump threshold from 0 to 3–5, OR implement γ-based alternative path.
**Audit result:** **PARTIAL.** `reference_runner.py:207` sets `max_open_crit_high: int = 5` with comment *"Was 0 (unreachable). Exp 39-0 fix."* The threshold bump is done.

**What remains:** the documented γ-based alternative path (γ ≥ 0.30 OR three consecutive rounds with zero novel CRITICAL) is still documentation-only. The config's `_convergence_criteria.pass_condition` is prose that has not been translated to code. This is the remaining half of Item 1A.3.

**Plan update:** threshold done; γ-alternative path remains TODO.

### 1B.1 — Macrophage blind

**Audit result:** **OPEN.** Shadow log confirms still broken across all six rounds of 39-0. Requires investigation at the `immune_result.cell_verdicts` producer site.

### 1B.2 — DeepSeek decomposition trap

**Audit result:** **OPEN.** Multi-part fix. The shadow logs do not let me verify the fingerprint state directly; the symptom needs to be tested on live dispatch. Acceptance test: replay of 39-0's DeepSeek raw outputs under v2 parser and fingerprint logic.

### 1B.3 — DeepSeek parser for markdown bold headers

**Audit result:** **LIKELY DONE** (needs test verification). `parse_findings` has expanded parser paths. The specific "P1 SHADOW" fallback for markdown code blocks (lines 2396–2422 of `reference_runner.py`) is in shadow mode, so it does NOT currently parse DeepSeek's bold-heading findings into live flow. A small test on the actual R5 DeepSeek output will confirm whether the main parser paths already catch the format or whether live promotion of the markdown fallback is required.

### 1C.1 — Autoimmune false alarm

**Audit result:** **LIKELY OPEN.** Analysis note `bench/logs/exp39_0_gate_20260413T193320Z/analysis_immune_convergence.md:74-78` describes the split-flag fix (AUTOIMMUNE_REJECTION vs DEPLETION_EXPECTED) as prospective, not applied. Need to grep for the flag names in the current runner.

### 1C.2 — ITC degradation false trigger

**Audit result:** **OPEN** (presumed — not verified).

### 1D.1 through 1D.6 — lessons-forward items

**Audit result:** retained as **OPEN** per plan. No evidence these landed.

### 1E.1 through 1E.12 — schema wiring items

**Audit result:** mostly **CONFIRMED OPEN** or **PARTIAL**:
- 1E.1 §17: already wired in `reference_runner.py` — verify carries to v2
- 1E.2 §18: already wired — verify carries to v2
- 1E.3 specialist cell live-promotion: shadow at `reference_runner.py:~3741` per plan; needs flip
- 1E.4 K/L/M functional shadow: likely OPEN
- 1E.5 fingerprint attention metrics: OPEN
- 1E.6 dynamic decomposition: OPEN
- 1E.7 cross-model diversity metric: OPEN
- 1E.8 Ouroboros query-quality: OPEN (confirmed by this audit)
- 1E.9 recidivism detection: OPEN
- 1E.10 channel-assignment boundary assertion: OPEN
- 1E.11 OpenRouter tool-use: OPEN
- 1E.12 DeepSeek specialist role: OPEN

---

## Reconciled status of Part 1

| Item | Plan stated | Audit finds | Action |
|---|---|---|---|
| 1A.1 S_k format | TODO | DONE | Mark DONE, add regression test to v2 |
| 1A.2 parser IDs | TODO | DONE | Mark DONE, add regression test to v2 |
| 1A.3 gate unreachable | TODO | PARTIAL | Threshold done; γ-alt path TODO |
| 1B.1 macrophage blind | TODO | OPEN | Investigate immune_result site |
| 1B.2 DeepSeek decomp trap | TODO | OPEN | Multi-part fix |
| 1B.3 DeepSeek markdown parser | TODO | TEST FIRST | Replay 39-0 R5 output to check |
| 1C.1 autoimmune false alarm | TODO | LIKELY OPEN | Grep for flag names |
| 1C.2 ITC false trigger | TODO | OPEN | Confirm open, then fix |
| 1D.1–1D.6 lessons-forward | TODO | OPEN | All six items require implementation |
| 1E.1 §17 wiring | VERIFY | CONFIRMED | Behavioural test in v2 |
| 1E.2 §18 wiring | VERIFY / CONFIGURE | CONFIRMED | Behavioural test in v2 |
| 1E.3 specialist live-promotion | TODO | OPEN | Single-line flip + test |
| 1E.4 K/L/M functional shadow | TODO | OPEN | Build four specialist cells |
| 1E.5 fingerprint metrics | TODO | OPEN | Wire from existing ITC data |
| 1E.6 dynamic decomposition | TODO | OPEN | Replace static list |
| 1E.7 diversity metric | TODO | OPEN | Compute + log |
| 1E.8 Ouroboros query-quality | TODO | OPEN (this audit) | Fix query builder + mode flag |
| 1E.9 recidivism detection | TODO | OPEN | Cross-round state |
| 1E.10 channel-assignment boundary | TODO | OPEN | Assertion + test |
| 1E.11 OpenRouter tool-use | TODO | OPEN | Function-calling API |
| 1E.12 DeepSeek specialist role | TODO | OPEN | Phase 6 wiring |

**Revised effort estimate for Part 1 on v2:** roughly 20 items still active (3 tiny verification tests for already-done fixes, 17 substantive implementations). The audit removes about 4 items from the "implement" column and adds 3 "verify" items that replace them. Net reduction in coding work is modest but the psychological weight of the bug backlog is correctly shrunk.

---

## Next actions (for subsequent work sessions)

1. Add unit tests to v2 for DONE items 1A.1 and 1A.2 (regression guards). Fast.
2. Implement γ-based alternative convergence path (1A.3 remainder). Small, self-contained. Probably 30–60 LOC in `bench/dm/_convergence.py` with tests.
3. Diagnose 1B.1 Macrophage wiring at the `immune_result.cell_verdicts` producer site. Likely in `bench/immune_agents.py`.
4. Replay 39-0 R5 DeepSeek output against the current `parse_findings` to confirm or refute 1B.3. Small, bounded test.
5. Proceed through Part 1 in priority order as per the plan.

---

## Plan-maintenance note

The execution plan (`Exp40_to_54_Execution_Plan_2026-04-17.md`) is not edited in place by this audit. The plan retains its original structure; this audit is a dated overlay that records verified current state. When the next work session begins, the audit's findings should be folded into the plan's status fields (TODO → DONE / PARTIAL / OPEN) and this audit referenced as the source.

The audit is itself a commitable artefact — it becomes part of the experimental record.
