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

Opus 4.6 (Claude) and Codex 5.3 conducted 8 rounds of adversarial review. Gemini was then applied independently:
- Claude/Codex found ~24 issues across 8 rounds and converged
- Gemini found 16 novel issues that all 8 Claude/Codex rounds missed
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

**Infrastructure: PROVEN.** 21 API calls across 3 tasks, 3 conditions, zero INFRA_FAILs. Gemini 3.1 Pro is reliable when called directly via the `google.genai` SDK. The INFRA_FAILs in previous runs were caused by the subprocess layer (Claude/Codex CLI invocation for confer), not by the Gemini API itself.

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

**Methodological caveats** (Codex 5.3 infra review, 2026-03-21):
1. **Unbalanced n:** Control and CDSFL each had n=1 while PE had n=5. This means variance is measurable for PE only. Control and CDSFL scores are single data points, not means. Any cross-condition comparison is anecdotal at this sample size.
2. **ft-006 truncation confound:** All conditions hit the 16384-token output cap. Comparison is unreliable because truncation severity varied by condition. CDSFL may have been differentially affected (longer structured output hitting the cap earlier in proportional terms).
3. **Structural vs numerical scoring on ft-013:** The 8 binary criteria test whether values are structurally present, not whether they are numerically correct. A response could score 8/8 while containing incorrect calculations. This inflates apparent accuracy for well-structured responses.
4. **Assessor non-blinding:** Opus 4.6 acted as Tier 2 assessor while also being the system that designed the CDSFL framework. The assessor is not blind to condition and has a structural interest in the outcome. Independent human assessment or blind automated scoring should supplement these results.

---

## Planned Experiments

### Experiment 3: Full Gemini Frontier Run (25 tasks)

**Status:** Planned — pending diagnostic completion
**Model:** gemini-3.1-pro-preview
**Task set:** Full 25-task frontier set
**Conditions:** Control, PE, CDSFL (as per diagnostic design)
**Orchestrator:** Opus 4.6 (Claude) via CLI
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

| Condition | Findings | Critical | Major | Minor | Avg Conf | Gemini | Codex | Merkle Root |
|-----------|----------|----------|-------|-------|----------|--------|-----|-------------|
| Control | 19 | — | — | — | — | — | — | `186e39bc...` |
| HIL | 2 | 0 | 1 | 0 | 0.93 | 0 | 1 | `62594df9...` |
| CDSFL | 10 | 2 | 4 | 4 | 0.88 | 3 | 3 | `2a4e6509...` |
| CDSFL+HIL | 27 | 17 | 10 | 0 | 0.95 | 9 | 18 | `38cb6006...` |

Corpus hash: `ad66ba3d82edd205...`
Directives hash: `cec89b733c3f4259`
All four hash chains verified valid.

##### Gemini 3.1 Pro (SDK) — CDSFL+HIL Only

| Condition | Findings | Critical | Major | Minor | Avg Conf | Gemini | Codex | Merkle Root |
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
- Gemini failure policy: kill → retry → progressive prompt reduction × 5 → halt and diagnose with Codex.
- Zero API cost (CLI subscriptions). Gemini API key on paid quota.
- **Sonnet confound (discovered 2026-03-22):** Claude solution generation and arbiter assessments in this smoke test used Sonnet 4.6 (the `claude -p` default), not Opus 4.6 as documented. The `--model` flag was not specified. This affects solution quality and arbiter judgment but does not invalidate the cross-condition comparisons (the same model was used consistently across all four conditions). Corrected for Phase 2.
- **API key billing confound (discovered 2026-03-22):** `.env` contained `ANTHROPIC_API_KEY`, causing `claude -p` to use pay-per-token API credits instead of the existing subscription. This generated "credit balance too low" warnings and unnecessary cost. The key was removed; Phase 2 uses subscription authentication.

**Raw data:** `bench/results/round_robin/` (Gemini 3), `bench/results/round_robin_31pro/` (Gemini 3.1 Pro)
**Smoke test record:** `bench/results/round_robin/SMOKE_TEST_RECORD.md`
**Activity logs:** `bench/logs/round_robin_smoke_*.log`

#### Phase 1 (Pilot — Stateless Invocation)

**Status:** 12 runs completed (2026-03-21). Retained as pilot data.
**Delivery mechanism:** Stateless per-step invocation. Each model call was independent — no accumulated context between steps.
**Tasks completed:** ft-001, ft-002, ft-003 × 4 conditions each.
**Raw data:** `bench/results/round_robin/`

Phase 1 revealed two methodological confounds:

1. **Stateless invocation confound:** Stateless per-step invocation conflates "model cannot solve this problem" with "model cannot solve this problem when presented as a monolithic block with no context accumulation." This was discovered when Codex 5.3 produced zero output on ft-004 under stateless invocation but completed all 8 steps under persistent-conversation tutor-style decomposition (Experiment 5 below).

2. **Model identity confound (Sonnet/Opus):** The `claude -p` invocations used to generate Claude solutions and arbiter assessments did not specify `--model`. The Claude CLI defaults to Sonnet 4.6, not Opus 4.6. Every Phase 1 result labelled "Opus 4.6" was in fact generated by Sonnet 4.6 — a model optimised for speed and everyday tasks, not deep multi-step mathematical reasoning. This was not discovered until Phase 2 preparation (2026-03-22), when the founder identified the discrepancy by testing `claude -p` directly and observing Sonnet self-identifying. The `--model claude-opus-4-6` flag was added for Phase 2. Additionally, the `.env` file contained an `ANTHROPIC_API_KEY` that caused `claude -p` to use pay-per-token API credits instead of the existing subscription, generating spurious "credit balance too low" warnings and unnecessary cost.

Both confounds are documented here as errors of the experimenter, not suppressed. Phase 1 data remains valid as pilot data about Sonnet 4.6 + Gemini 3.1 Pro + Codex 5.3 performance under stateless conditions. It is NOT pooled with Phase 2 data, which uses the correct model (Opus 4.6) and correct authentication (subscription).

#### Experiment 5: Tutor-Style Decomposition Validation (ft-004)

**Date:** 2026-03-22
**Models:** Gemini 3.1 Pro Preview (SDK, multi-turn chat), Codex 5.3 (codex exec, accumulated context)
**Orchestrator/Tutor/Arbiter:** Opus 4.6 (Claude)
**Task:** ft-004 — Continuous Nowhere-Differentiable Function (Weierstrass construction)
**Purpose:** Validate persistent-conversation tutor-style decomposition as delivery mechanism for Phase 2.

##### Motivation

ft-004 caused failures under all prior delivery mechanisms:
- Claude monolithic: timed out at 900s and 1200s
- Claude decomposed (stateless solve→attack→revise): completed at 600s/step but crude
- Codex stateless per-step: zero output
- Gemini stateless per-step: completed but no context accumulation

The hypothesis: these failures reflect working-memory overload from monolithic presentation, not capability limitations. Standard pedagogical practice (sequential revelation with context accumulation) should resolve them.

##### Design

Eight tutor steps, each building on the model's own prior answers in a persistent conversation:

1. **Setting** — what does continuous-but-nowhere-differentiable mean?
2. **Construction** — why each parameter condition (0 < a < 1, b odd, ab > 1 + 3π/2)?
3. **Continuity proof** — uniform convergence via Weierstrass M-test
4. **Construct x_m** — explicit sequence approaching arbitrary x
5. **Bound dominant term** — m-th term contribution ≥ C·(ab)^m
6. **Bound head and tail** — remaining terms bounded or reinforcing
7. **Combine and conclude** — recover the Weierstrass condition
8. **Self-verification** — model checks its own complete proof

Each prompt explicitly references the model's prior work ("use YOUR construction from step 4a," "use YOUR values of C and C'"). The tutor controls the pace of revelation; the model accumulates understanding.

Gemini used native SDK multi-turn chat (`client.chats.create()`). Codex used accumulated conversation history prefixed to each `codex exec` call (stateless API, simulated persistence).

##### Results

| Model | Steps Complete | Time | C (dominant) | Sufficient Condition | Self-Verification |
|-------|---------------|------|--------------|---------------------|-------------------|
| Gemini 3.1 Pro | 8/8 | 219.5s | 2/3 | ab > 1 + 3π/2 ≈ 5.71 | Complete, 1 issue found (boundary domain) |
| Codex 5.3 | 8/8 | 574.7s | 1 | ab > 1 + π ≈ 4.14 | Complete, 3 issues found (sum-limit interchange, boundary subcases, notation) |

Both models completed all 8 steps. Codex went from total failure (zero output under stateless invocation) to full completion with a mathematically sharper result.

##### Critical Finding: Independent Constructions

The two models independently chose different constructions for x_m:

- **Gemini** chose ε_m with **opposite** sign to e_m. This gives |ε_m − e_m| ∈ [1, 3/2], so the dominant term bound is C = 1/(3/2) = 2/3. The sufficient condition becomes ab > 1 + 3π/2 — recovering the classical Weierstrass bound.

- **Codex 5.3** chose σ_m with **same** sign as e_m. This gives |σ_m − e_m| ∈ [1/2, 1], so the dominant term bound is C = 1/1 = 1. The sufficient condition becomes ab > 1 + π — strictly sharper than the classical bound.

Both algebraic derivations computationally verified (initially via Wolfram Alpha, subsequently via SymPy). Codex's construction is a valid improvement over the classical Weierstrass proof: the same-sign approach direction keeps the denominator smaller, producing a tighter lower bound that relaxes the sufficient condition. Codex identified this in its own self-verification: "Not a correctness failure; it reflects a sharper estimate from my x_m choice."

Neither bound is novel in absolute terms — Hardy (1916) proved the theorem for ab ≥ 1 — but the fact that tutor-style decomposition produced two independent, valid proofs with different constructions validates the approach for multi-architecture review: you get genuine mathematical diversity, not stylistic variation.

##### Implications for Phase 2

1. **Delivery mechanism validated:** Persistent conversation with sequential decomposition resolves the working-memory confound that caused Phase 1 failures.
2. **Multi-architecture diversity confirmed:** Different models produce genuinely different mathematical approaches under the same pedagogical structure.
3. **Self-verification is meaningful:** Both models identified real issues in their own proofs when given full context (impossible under stateless invocation).

**Codex 5.3 P-Pass of this methodology change** (2026-03-22): Codex raised 5 findings. Key accepted items: (1) persistent conversation + decomposition is a confounded intervention (acknowledged — architecturally coupled, separable in follow-up study), (2) Phase 1 must be strictly excluded from confirmatory analysis (agreed), (3) smoke test should cover multiple domains (accepted — expanded to 3 tasks). Key rejected items: (4) "hidden fifth factor" — delivery mechanism change is uniform across all 4 conditions, so within-Phase-2 factorial comparisons remain valid.

**Raw data:** `bench/results/tutor_test/ft-004_tutor_v2_20260322_044718.json`
**Codex P-Pass:** `bench/results/cx_ppass_methodology_change.txt`

#### Phase 2 (Main Experiment — Persistent Conversation)

**Status:** Pending smoke test validation. 25 tasks × 4 conditions = 100 runs.
**Delivery mechanism:** Persistent-conversation tutor-style decomposition. Each model maintains full context across all steps of a task.
**Smoke test plan:** 3 tasks (1 maths, 1 code, 1 cross-domain) × 4 conditions = 12 runs, to validate infrastructure before full run.
**Estimated duration:** 30-50 hours (checkpoint/resume across sessions).
**Design:** Same 2×2 factorial as Phase 1 (Control / HIL / CDSFL / CDSFL+HIL). Phase 1 data is not pooled.

##### Methodology Change Record

The change from stateless to persistent-conversation invocation was prompted by observed failure (Codex zero output on ft-004) and the hypothesis that the failure was architectural (working memory overload), not capability-related. This was confirmed when the same model completed the same task under persistent-conversation delivery.

This is standard experimental practice: a pilot phase reveals a methodological flaw, the flaw is corrected, the correction is documented, and both phases are reported. The pilot data is valid as pilot data. The corrected methodology is the main experiment. The correction itself is a finding: delivery mechanism significantly affects model performance independent of prompt content.

**What changed:**
1. How prompts are delivered (stateless → persistent conversation with sequential decomposition).
2. Claude model corrected from Sonnet 4.6 (CLI default) to Opus 4.6 (`--model claude-opus-4-6`).
3. Authentication corrected from API key (pay-per-token) to subscription (no per-token cost).

**What did not change:** The 2×2 factorial design, the task set, the reviewer models (Gemini 3.1 Pro, Codex 5.3), the scoring criteria, the confer protocol, the cryptographic verification, the stop rules.

**Command:** `python3 bench/run_round_robin.py --phase2`

##### Phase 2 Smoke Test 1 Results (2026-03-22)

**Status:** Incomplete — 7 of 12 runs completed before artificial 90-minute budget expired.
**Tasks completed:** ft-001 (all 4 conditions), ft-006 (3 of 4 conditions — CDSFL+HIL never ran).
**Tasks not reached:** ft-013 (Solar-Powered Water Purification).

| Task | Condition | HARD findings | Rounds | Notes |
|------|-----------|--------------|--------|-------|
| ft-001 | Control | 1 | 3 | Opus solution strong — few errors to find |
| ft-001 | HIL | 0 | 2 | Findings classified SOFT, not HARD |
| ft-001 | CDSFL | 0 | 2 | Same — little to find in correct proof |
| ft-001 | CDSFL+HIL | 0 | 2 | Same — but expert guidance was generic |
| ft-006 | Control | 10 | 5 | Both reviewers productive all 5 rounds |
| ft-006 | HIL | 0 | 2 | Findings classified SOFT |
| ft-006 | CDSFL | 10 | 5 | Both reviewers productive all 5 rounds |
| ft-006 | CDSFL+HIL | — | — | **NEVER RAN** (budget expired) |

**Critical gaps in this data:**

1. **CDSFL+HIL never ran on the productive task (ft-006).** The most important data point is missing. No conclusions can be drawn about the interaction effect from this smoke test.

2. **Expert guidance was generic.** The HIL_EXPERT_GUIDANCE_PROMPT asked Claude to provide "common failure modes" and "domain-specific knowledge" — generic instructions that produced generic guidance. For ft-001, genuine expert guidance would name specific theorems, cite specific conditions, and target specific proof steps. This has been corrected: the prompt now requires research-level domain expertise with named theorems, specific bounds, verification targets, edge cases, and cross-references.

3. **90-minute budget was experimenter error.** The founder explicitly stated "I don't care if it takes 2 or 3 days." The budget was an optimisation for quick validation that killed the experiment prematurely. Removed for all subsequent runs.

4. **HARD/SOFT classification may be too aggressive.** HIL and CDSFL+HIL conditions produced raw findings (visible in logs) that were classified as SOFT. Whether the classification threshold is appropriate requires manual review of the finding content.

**Issues identified and fixed for smoke test 2:**

1. **API key vs subscription auth:** `.env` contained `ANTHROPIC_API_KEY`, causing `claude -p` to use pay-per-token API instead of subscription. Script now actively removes this key from environment at startup with a warning.

2. **Budget cap removed:** No artificial time limits. Runs until complete or killed.

3. **Expert guidance upgraded:** Prompt rewritten to demand research-level domain expertise — named theorems, specific bounds, verification targets, edge cases, cross-references.

4. **Codex code review findings (12 issues fixed):** GeminiReviewChat.send() now enforces timeout and has 5-attempt retry policy raising GeminiExhausted. Phase 2 chat init fails hard (no silent fallback to stateless). Env validation skips gemini CLI check in Phase 2 (uses SDK). Cost-cap early return includes condition field.

5. **Sonnet/Opus model identity:** Already corrected in Phase 2 (`--model claude-opus-4-6`), confirmed working.

**Raw data:** `bench/results/round_robin_phase2/round_robin_results.json`
**Activity log:** `bench/logs/round_robin_phase2_smoke_20260322T065109Z.log`

##### The Inverse Square Root Law as Chatbot Diagnostic (2026-03-23)

The Inverse Square Root Law of Precision (standard error = σ/√n) predicts that each additional measurement yields diminishing returns. The marginal information gain from the n-th measurement decreases as 1/√n. To halve the error, you must quadruple the measurements. This is the mathematical foundation of diminishing returns in data collection, and it applies directly to iterative review: each additional review round should find fewer novel issues than the previous round, because the easy-to-find issues are exhausted first.

In plain terms: if you keep rolling a ball up an ever steeper hill, eventually the work you put in will clearly outweigh the reward for your effort.

This provides a built-in diagnostic for distinguishing genuine analysis from chatbot churn:

- **Genuine analysis** produces a convergent curve: round-over-round findings decrease, following inverse square root decay or faster. Codex 5.3 on ft-001/CDSFL: 5 → 3 → 2 → 2 → 0. This is a model exhausting a finite set of real issues.

- **Chatbot churn** produces a flat or near-flat line: constant output regardless of whether anything remains to find. DeepSeek V3 on ft-001/Control: 2 → 2 → 2 → 2. This is a model producing output because it is expected to, not because there is something to find. It violates the inverse square root law, which all genuine measurement processes obey.

A model that produces "2 new findings" in every round while simultaneously stating "concur_stop=True" (I agree we should stop) is exhibiting contradictory behaviour characteristic of engagement-optimised chatbots: generate content because you are asked to, agree to stop because you are asked if you should.

This observation has direct implications for the CDSFL framework: the G_n formula already models diminishing returns via geometric decay with the correlation parameter ρ. Models that violate this decay pattern are not providing independent measurements — they are generating noise. The SymPy verification kernel (CDSFL conditions only) provides a second diagnostic: what fraction of a model's findings are computationally verified as correct, versus what fraction are plausible-sounding but false? A model with a flat finding curve AND a low verification rate is producing pure churn.

**Methodological note:** The inverse square root law assumes independent, identically distributed measurements. When reviewers are correlated (high ρ), returns diminish faster. Architectural diversity between reviewers (different model families, different training data) reduces ρ, which is the biodiversity hypothesis restated in statistical terms.

##### Phase 2 Smoke Test with DeepSeek V3 (2026-03-23)

**Change from Smoke Test 1:** Gemini 3.1 Pro replaced with DeepSeek V3 (`deepseek-chat` via OpenAI-compatible API). Gemini was a generalist chatbot with no reasoning-optimised variant available — weak baseline for falsification tasks. DeepSeek V3 provides a different architecture (MoE, different training corpus) for stronger biodiversity.

**Additional changes:**
- HIL guidance capped at 500 characters maximum (realistic human expert input, not machine-generated exhaustive briefing)
- Condition isolation enforced: external research (SymPy, arXiv, web) available to CDSFL and CDSFL+HIL only, not HIL alone
- HIL prompt simplified to approximate a competent human providing brief expert guidance from their own knowledge — not an idealised 7,800-character domain briefing

**Status:** Complete (6 of 12 runs — ft-013 not reached before test stopped for design revision).

**Results summary:**

| Condition | Runs | HARD findings | Avg rounds |
|-----------|------|---------------|------------|
| Control | 2 | 37 | 5.0 |
| HIL | 2 | 0 | 1.0 |
| CDSFL | 1 | 22 | 5.0 |
| CDSFL+HIL | 1 | 20 | 5.0 |

**Decay curve analysis (per-model, per-round novel finding counts):**

| Task/Condition | DeepSeek V3.2 | Pattern | Codex 5.3 | Pattern |
|----------------|--------------|---------|-----------|---------|
| ft-001/Control | 5,4,0,2,2 | Non-monotone | 0,1,0,0,0 | Near-zero |
| ft-001/HIL | 1,0 | — | 0,0 | — |
| ft-001/CDSFL | 2,2,2,2,2 | **Flat** | 5,3,2,2,0 | **Decay** |
| ft-001/CDSFL+HIL | 6,3,4,2,2 | Non-monotone | 3,0,1,1,0 | Decay (noisy) |
| ft-006/Control | 5,4,4,5,5 | **Flat** (~4.6) | 4,2,0,0,0 | **Steep decay** |

**Key findings:**

1. **CDSFL activates Codex but not DeepSeek.** Codex under Control on ft-001 found almost nothing (0,1,0,0,0). Under CDSFL on the same task: 5,3,2,2,0. The methodology activated dormant capability. DeepSeek showed no such activation — flat output regardless of condition.

2. **Decay curve diagnostic validated.** Codex consistently produced convergent decay curves (genuine analysis). DeepSeek consistently produced flat or non-monotone curves (chatbot churn). The ft-001/CDSFL comparison is the clearest: DeepSeek produced exactly 2 findings per round for 5 rounds (perfectly flat), while Codex produced a textbook decay curve.

3. **HIL found zero HARD findings.** Both runs, both tasks. The 500-character guidance cap correctly prevented the over-powered HIL condition from earlier smoke tests.

4. **Control HARD finding count (37) is likely inflated by churn.** DeepSeek contributed most of the Control findings with flat curves, suggesting many are not genuine. Without SymPy verification on Control conditions, the raw count is unreliable.

5. **Wolfram-verified mathematical framework (AICc model comparison):**
   - Codex ft-001/CDSFL data fitted to exponential (AICc=2.88), power law (4.88), logarithmic (6.69), constant (8.18). Exponential best fit. D = 0.667 (half-life 1.5 rounds).
   - DeepSeek ft-001/CDSFL: lambda = 4.1e-17 (effectively zero). D = 0. Constant model fits perfectly.
   - F-test: Codex decay vs flat, F=29.87, p=0.012 (indicative at n=5, requires bench test confirmation).

**Design revision prompted by these results:**
- CC (Opus 4.6) added as third reviewer in blind and confer rounds (was orchestrator/arbiter only — insufficient for biodiversity testing with only one genuine analyst)
- Three-way confer topology: each reviewer sees the other two's findings
- (D, v̄, A, C) capability fingerprint framework adopted for computational assessment

**Raw data:** `bench/results/round_robin_phase2/round_robin_results.json`
**Activity log:** `bench/logs/round_robin_phase2_deepseek_20260323T000340Z.log`

---

*Raw data for all experiments is stored in `bench/results/`. This document is the interpretive record. For the technical methodology, see the [white paper](../PAPER.md). For the experimental design rationale, see the [experiment plan memory file](../../.claude/projects/-Users-georgejackson-Developer-Projects/memory/cdsfl_experiment_plan.md). For the full experimental methods, see [PAPER.md Part X-A — Experimental Methods](../PAPER.md).*
