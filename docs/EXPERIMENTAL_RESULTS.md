# CDSFL Experimental Results

**Status:** Active — results recorded as experiments complete.

This document is the canonical record of all empirical testing of the CDSFL methodology. Each experiment is recorded with full methodology, raw data references, and findings — including null results and failures. Nothing is omitted.

---

## Prior Experiments (pre-formal recording)

The following experiments were conducted before this results document was established. Summaries are reconstructed from commit history, MEMORY.md, and session records. Raw data for these experiments exists in `bench/results/` but was not formally written up at the time.

### Experiment 0: Four-Condition Self-Test

**Date:** March 2026 (pre-2026-03-18)
**Model:** Claude Code (Opus 4.6)
**Task set:** Seeded-fault benchmark (code review)

Four conditions tested:
1. **Control** — no methodology
2. **CDSFL only** — full framework, no domain expertise
3. **HIL only** — domain expertise, no framework
4. **CDSFL + HIL** — full framework with domain expertise

**Key finding:** All single-invocation conditions capped at approximately the same recall rate regardless of methodology. Iterative multi-pass review with expert direction achieved complete coverage. Implication: there exists a complexity threshold below which methodology formalisation adds no measurable detection value. Iteration, not single-pass structure, is load-bearing.

**Raw data:** `bench/results/` (pre-Phase 2 files)

### Experiment 1: Three-Architecture Adversarial Review

**Date:** 2026-03-18
**Models:** Claude Code (Opus 4.6), Codex (5.3), Gemini
**Scope:** Full codebase + methodology review

CC/CX conducted 8 rounds of adversarial review. Gemini was then applied independently:
- CC/CX found ~24 issues across 8 rounds and converged
- Gemini found 16 novel issues that all 8 CC/CX rounds missed
- Gemini Extended P-Pass (5 modules) found additional issues

**Key finding:** Heterogeneous architectures find defects that homogeneous review misses — validates the biodiversity hypothesis. Convergence curves were different. Failure modes were different. Epistemic diversity is not redundancy; it is additional compute.

**Commits:** `afcc323` (main review), see MEMORY.md for full commit trail
**Raw data:** `~/Desktop/Accessibility/CE_Gemini_EPP_Module{1-5}_2026-03-18.txt`

---

## Formal Experiments

### Experiment 2: Gemini 3.1 Pro Diagnostic Run

**Date:** 2026-03-20
**Model:** gemini-3.1-pro-preview (Google, Paid Tier 1 API)
**Orchestrator/Assessor:** Claude Code (Opus 4.6), acting as Tier 2 domain expert
**Purpose:** Validate infrastructure, establish calling patterns, generate pilot dataset before full 25-task frontier run
**SDK:** google-genai 1.67.0 (migrated from deprecated google-generativeai)

#### Design

Three frontier tasks spanning different domains:
- ft-001: mathematics/proof (Erdős–Szekeres theorem) — expected 40–50% single-pass
- ft-006: software/code (Interval Scheduling with Weighted Dependencies) — expected 20–30% single-pass
- ft-013: cross-domain/design (Solar-Powered Water Purification System) — expected 20–30% single-pass

Three conditions per task:
1. **Control** — raw prompt, no system instruction. 1 run.
2. **Prompt Engineering (PE)** — competent human-level prompting ("think carefully, show reasoning, double-check"). Not CDSFL. Not leading the model. 5 runs per task (to measure variance).
3. **CDSFL** — full framework: HARD/SOFT constraint classification, P-Pass self-falsification, epistemic marking, structured output. 1 run (further passes on assessor judgment).

#### Infrastructure

- All calls made via Google GenAI SDK (`google.genai`), not deprecated `google.generativeai`
- `max_output_tokens`: 16384
- HTTP timeout: 300s (5 min)
- Inter-call spacing: 3s (rate limit buffer)
- No model fallback — Gemini 3.1 Pro or failure recorded
- Error protocol: diagnose, adapt prompt, retry up to 5 cycles, then stop and report

#### Results: ft-001 (Erdős–Szekeres Theorem)

Nine binary scoring criteria derived from ground truth (labelling definition, uniqueness proof, pigeonhole bounds, monotonicity bridge, correct 16-element construction, proofs of no length-5 subsequences, length-4 exhibition, no wrong-length error).

| Condition | Run | Score | Pct | Latency | Response |
|-----------|-----|-------|-----|---------|----------|
| Control | 1 | 8/9 | 89% | 62.4s | 6,342 ch |
| PE | 1 | 9/9 | 100% | 68.8s | 6,135 ch |
| PE | 2 | 7/9 | 78% | 42.9s | 6,015 ch |
| PE | 3 | 8/9 | 89% | 49.5s | 5,850 ch |
| PE | 4 | 6/9 | 67% | 57.9s | 6,142 ch |
| PE | 5 | 8/9 | 89% | 50.5s | 6,066 ch |
| CDSFL (initial) | 1 | 9/9 | 100% | — | — |
| CDSFL (revised) | 1 | 9/9 | 100% | 101.8s | 11,414 ch |

**Condition averages:**

| Condition | Mean | Range | Latency | Size |
|-----------|------|-------|---------|------|
| Control | 89% | 89–89% (n=1) | 62.4s | 6,342 ch |
| PE | 84.4% | 67–100% (n=5) | 53.9s | 6,042 ch |
| CDSFL | 100% | 100–100% (n=1) | 101.8s | 11,414 ch |

**CDSFL self-falsification quality:** Gemini identified 3 genuine tightening points in its own initial answer: (1) implicit pigeonhole in Part 2 proof, (2) verification by enumeration rather than mathematical demonstration, (3) monotonicity/distinctness bridge unstated. All three are legitimate. Revised answer addressed all three.

**PE variance:** 33-percentage-point spread across 5 identical PE runs (67%–100%). "Think carefully" did not consistently improve output and may have introduced instability relative to the unguided control.

**Infrastructure:** Zero INFRA_FAILs across 7 API calls. Gemini 3.1 Pro is stable when called correctly via the new SDK without subprocess contamination.

**Scoring limitations:** Pattern-based automated scoring produced some false negatives (e.g., uniqueness proof present but using variable names the regex missed). Manual review must supplement automated scoring for subsequent tasks.

**Assessor note:** This task is at the easier end of the frontier set (40–50% expected). The Erdős–Szekeres theorem is well-known and likely in training data. Differential effects between conditions are predicted to be larger on harder, less-trained tasks. The PE variance signal is potentially more informative than the mean scores at this difficulty level.

#### Results: ft-006 (Interval Scheduling — software/code)

**Critical finding: output truncation.** Every response across all conditions hit `FinishReason.MAX_TOKENS` at the 16384-token output cap. Code generation tasks at frontier difficulty exceed this limit. The CDSFL response (10,065 chars) and most PE runs appeared to reach code completion despite truncation, but the control (2,958 chars) and PE run 5 (2,102 chars) were cut off mid-code. This makes fair comparison unreliable for this task.

| Condition | Run | Chars | Finish | Truncated mid-code? |
|-----------|-----|-------|--------|---------------------|
| Control | 1 | 2,958 | MAX_TOKENS | Yes — cut mid-function |
| PE | 1 | 6,360 | MAX_TOKENS | No — reached code end |
| PE | 2 | 8,688 | MAX_TOKENS | No — reached code end |
| PE | 3 | 6,910 | MAX_TOKENS | No — reached code end |
| PE | 4 | 8,194 | MAX_TOKENS | No — reached code end |
| PE | 5 | 2,102 | MAX_TOKENS | Yes — cut mid-sort |
| CDSFL | 1 | 10,065 | MAX_TOKENS | No — reached code end |

**CDSFL structural compliance:** All four markers present. Constraint classification, self-falsification, and revised answer all generated despite truncation.

**Latency:** Control 141.5s, PE mean 194.0s, CDSFL 212.6s. Significantly slower than maths/design tasks — code generation is compute-intensive.

**Action required for full run:** Increase `max_output_tokens` to 32768 or higher for code tasks. Alternatively, accept truncation as a variable and record it. The truncation itself is data: CDSFL produces more structured output that reaches functional completion within the same token budget more reliably than unstructured conditions.

**Scoring: deferred.** Automated scoring against ground truth (run code, check test case outputs) requires non-truncated, executable code. Manual review of the CDSFL response shows it produced a complete algorithm with dependency DAG handling, but the control response is too truncated to compare fairly. This task should be re-run with higher output limits.

#### Results: ft-013 (Solar Water Purification — cross-domain/design)

Eight binary scoring criteria derived from ground truth: concentrate-end osmotic pressure (the key failure mode), operating pressure range, feed flow calculation, 40% recovery acknowledgment, specific energy consumption, solar array sizing, battery storage, membrane element count.

| Condition | Run | Score | Pct | Latency | Response |
|-----------|-----|-------|-----|---------|----------|
| Control | 1 | 7/8 | 88% | 76.2s | 6,880 ch |
| PE | 1 | 8/8 | 100% | 90.6s | 7,694 ch |
| PE | 2 | 8/8 | 100% | 96.8s | 7,113 ch |
| PE | 3 | 8/8 | 100% | 59.6s | 7,725 ch |
| PE | 4 | 8/8 | 100% | 96.7s | 7,135 ch |
| PE | 5 | 8/8 | 100% | 89.1s | 7,120 ch |
| CDSFL (initial) | 1 | 8/8 | 100% | — | — |
| CDSFL (revised) | 1 | 8/8 | 100% | 96.3s | 10,326 ch |

**Condition averages:**

| Condition | Mean | Range | Latency | Size |
|-----------|------|-------|---------|------|
| Control | 88% | 88% (n=1) | 76.2s | 6,880 ch |
| PE | 100% | 100–100% (n=5) | 86.5s | 7,357 ch |
| CDSFL | 100% | 100% (n=1) | 96.3s | 10,326 ch |

**Assessment:** Near-ceiling performance across all conditions. Gemini 3.1 Pro handles this cross-domain engineering task well — the "primary failure mode" identified in ground truth (incorrect osmotic pressure at concentrate end) was avoided even by the control condition. The automated scoring is structural (is the value present?) not quantitative (is the value correct?). Manual verification of the numerical calculations is needed to determine whether the scores reflect genuine engineering accuracy or merely structural completeness.

**PE variance:** Zero variance across 5 runs (all 100%). Contrasts sharply with ft-001 where PE variance was 33 points. This suggests PE stability may be domain-dependent — engineering design tasks may have more deterministic solution paths than mathematical proofs.

**CDSFL self-falsification:** All four structural markers present. The CDSFL response was 50% larger than PE average, with the additional content being constraint classification and self-falsification. Quality of the self-falsification findings needs manual review — on a near-ceiling task, the value of self-falsification may be in identifying edge cases and design robustness rather than correcting errors.

#### Diagnostic Summary

**Infrastructure: PROVEN.** 21 API calls across 3 tasks, 3 conditions, zero INFRA_FAILs. Gemini 3.1 Pro is reliable when called directly via the `google.genai` SDK. The INFRA_FAILs in previous runs were caused by the subprocess layer (CC/CX CLI invocation for confer), not by the Gemini API itself.

**Output token limit: IDENTIFIED.** Code generation tasks hit the 16384-token cap. Must increase to 32768+ for the full run, or record truncation as a variable.

**CDSFL structural compliance: CONSISTENT.** All three CDSFL runs produced all four structural markers (CONSTRAINT_CLASSIFICATION, INITIAL_ANSWER, ISSUES_FOUND, REVISED_ANSWER). Gemini follows the framework without resistance.

**Automated scoring limitations: CONFIRMED.** Pattern-based scoring is too coarse for definitive conclusions. It catches structural presence/absence but not correctness. Manual review is essential, particularly for:
- Mathematical proofs (is the logic valid, not just present?)
- Engineering calculations (are the numbers correct, not just structurally placed?)
- Code (does it run and pass test cases?)

**Cross-condition findings:**

| Metric | ft-001 (maths) | ft-006 (code) | ft-013 (design) |
|--------|---------------|---------------|-----------------|
| Control | 89% | truncated | 88% |
| PE mean | 84% | truncated | 100% |
| PE variance | 33 pts | — | 0 pts |
| CDSFL | 100% | structural OK | 100% |
| CDSFL self-falsification | 3 genuine issues | present | present |
| INFRA_FAILs | 0 | 0 | 0 |

**Key observations:**
1. PE variance is domain-dependent: high in maths (33 pts), zero in engineering design. "Think carefully" is unreliable on proof tasks.
2. CDSFL produces consistently structured output regardless of domain — the framework imposes discipline that bare prompting does not.
3. All three tasks may be too easy for Gemini 3.1 Pro to show large differential effects. The expected single-pass accuracy for these tasks was 20–50%; Gemini exceeded expectations across the board. Harder tasks or manual quality assessment may be needed to discriminate between conditions.
4. The CDSFL response is consistently ~50–90% larger than PE/control, with the additional content being constraint classification and self-falsification. Whether this additional content adds value depends on the domain and the complexity of the task.

**Methodological caveats** (CX infra review, 2026-03-21):
1. **Unbalanced n:** Control and CDSFL each had n=1 while PE had n=5. This means variance is measurable for PE only. Control and CDSFL scores are single data points, not means. Any cross-condition comparison is anecdotal at this sample size.
2. **ft-006 truncation confound:** All conditions hit the 16384-token output cap. Comparison is unreliable because truncation severity varied by condition. CDSFL may have been differentially affected (longer structured output hitting the cap earlier in proportional terms).
3. **Structural vs numerical scoring on ft-013:** The 8 binary criteria test whether values are structurally present, not whether they are numerically correct. A response could score 8/8 while containing incorrect calculations. This inflates apparent accuracy for well-structured responses.
4. **Assessor non-blinding:** CC (Opus 4.6) acted as Tier 2 assessor while also being the system that designed the CDSFL framework. The assessor is not blind to condition and has a structural interest in the outcome. Independent human assessment or blind automated scoring should supplement these results.

---

## Planned Experiments

### Experiment 3: Full Gemini Frontier Run (25 tasks)

**Status:** Planned — pending diagnostic completion
**Model:** gemini-3.1-pro-preview
**Task set:** Full 25-task frontier set
**Conditions:** Control, PE, CDSFL (as per diagnostic design)
**Orchestrator:** CC via CLI
**Budget:** $20 cap (Google API)

### Experiment 4: Round-Robin Distributed Compute Test

**Status:** Smoke test complete (2026-03-21). Full run approved.
**Models:** Opus 4.6 (orchestrator/arbiter), Gemini 3.1 Pro Preview (SDK), Codex 5.3 / GPT-5.3-codex (codex exec CLI)
**Task set:** 25 frontier tasks × 4 conditions = 100 runs

#### Design

2×2 factorial design testing two independent variables: structure (CDSFL framework) and guidance (domain expert HIL).

|  | No Structure | Full CDSFL Structure |
|--|--|--|
| **No Guidance** | Control | CDSFL |
| **Expert Guidance** | HIL | CDSFL+HIL |

Topology: Opus 4.6 orchestrates. Gemini 3.1 Pro and Codex 5.3 review independently (blind round 1), then confer (rounds 2-5, each sees the other's findings). Opus 4.6 arbitrates stop/continue. Both reviewers must concur with stop call. No concurrence after 5 rounds = defer for founder review.

Cryptographic verification: SHA-256 per-round input hashing, hash chain linking each record to predecessor, per-task Merkle root.

#### Smoke Test Results (2026-03-21)

**Task:** ft-001 — Monotone Subsequence Bound Tightening (mathematics)
**Gemini model:** Initial run with Gemini 3 (CLI), comparison run with Gemini 3.1 Pro Preview (SDK)

##### Gemini 3 (CLI) — All Four Conditions

| Condition | Findings | Critical | Major | Minor | Avg Conf | Gemini | CX | Merkle Root |
|-----------|----------|----------|-------|-------|----------|--------|-----|-------------|
| Control | 19 | — | — | — | — | — | — | `186e39bc...` |
| HIL | 2 | 0 | 1 | 0 | 0.93 | 0 | 1 | `62594df9...` |
| CDSFL | 10 | 2 | 4 | 4 | 0.88 | 3 | 3 | `2a4e6509...` |
| CDSFL+HIL | 27 | 17 | 10 | 0 | 0.95 | 9 | 18 | `38cb6006...` |

Corpus hash: `ad66ba3d82edd205...`
Directives hash: `cec89b733c3f4259`
All four hash chains verified valid.

##### Gemini 3.1 Pro (SDK) — CDSFL+HIL Only

| Condition | Findings | Critical | Major | Minor | Avg Conf | Gemini | CX | Merkle Root |
|-----------|----------|----------|-------|-------|----------|--------|-----|-------------|
| CDSFL+HIL | 22 | — | — | — | 0.96 | — | — | `95c98809...` |

##### Qualitative Analysis

**Depth vs churn:** Under control, confer rounds 3-5 rehash rounds 1-2 (same complaints reworded: "proof is missing," "proof is omitted," "proof is not shown"). Under CDSFL+HIL, confer rounds produce genuinely novel structural findings: "label-pair uniqueness proof not at full rigour," "pigeonhole arithmetic off-by-one conclusion unverified," "submission not self-contained — relies on unavailable external reference." The methodology produces deepening analysis, not volume.

**Methodology activates dormant capability:** Gemini contributed 0-3 findings under control/CDSFL/HIL but 9 substantive findings under CDSFL+HIL, including domain-specific catches ("must not use 'by construction' to bypass structural proofs," "must not conflate subsequence with contiguous substring"). Expert guidance transforms weaker model output.

**Interaction effect:** CDSFL+HIL (27 findings) exceeds CDSFL (10) + HIL (2) = 12. The combination produces findings neither component produces alone. The whole is greater than the sum of its parts.

**HIL alone is too focused:** Only 2 findings. Expert guidance narrows the search excessively, missing structural issues the framework catches.

##### P-Pass Assessment

The claim "these results are encouraging" survives falsification with caveats:
- n=1. Not statistically significant. The qualitative pattern (depth vs churn, methodology activation) is observable but not quantitatively established.
- ft-001 (Erdos-Szekeres) is in training data. Near-ceiling generation expected. These results validate the infrastructure and experimental design, not the methodology's performance on genuinely novel problems.
- Self-reviewing bias: Opus 4.6 generates solutions and arbitrates. Blind-pass design mitigates but does not eliminate.
- Nothing in these results says "stop." Nothing says "conclusive" either. The full 25-task run is required.

##### Extrapolation

Three falsifiable questions generated:
1. Does the CDSFL+HIL advantage persist on problems NOT in training data? (The specialist gap — only humans can supply test cases.)
2. Does the "methodology activates dormant capability" effect replicate with other weak models?
3. Is the depth-not-churn property of confer rounds specific to CDSFL+HIL, or does any structured iterative methodology produce it?

##### Infrastructure Notes

- Gemini CLI auth issue resolved by switching from OAuth to API key (`GEMINI_API_KEY`).
- Gemini upgraded from CLI (Gemini 3) to SDK (Gemini 3.1 Pro Preview) for stronger capability.
- Budget system corrected: no longer clamps individual subprocess timeouts (was strangling retries to 10s).
- Gemini failure policy: kill → retry → progressive prompt reduction × 5 → halt and diagnose with CX.
- Zero API cost (CLI subscriptions). Gemini API key on paid quota.

**Raw data:** `bench/results/round_robin/` (Gemini 3), `bench/results/round_robin_31pro/` (Gemini 3.1 Pro)
**Smoke test record:** `bench/results/round_robin/SMOKE_TEST_RECORD.md`
**Activity logs:** `bench/logs/round_robin_smoke_*.log`

#### Full Run

**Status:** Approved by founder (2026-03-21). 25 tasks × 4 conditions = 100 runs.
**Estimated duration:** 20-30 hours (checkpoint/resume across sessions).
**Command:** `python3 bench/run_round_robin.py`

---

*Raw data for all experiments is stored in `bench/results/`. This document is the interpretive record. For the technical methodology, see the [white paper](../PAPER.md). For the experimental design rationale, see the [experiment plan memory file](../../.claude/projects/-Users-georgejackson-Developer-Projects/memory/cdsfl_experiment_plan.md).*
