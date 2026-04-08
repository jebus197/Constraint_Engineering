# CDSFL Experimental Results

**Status:** Active — results recorded as experiments complete.

This document is the canonical record of all empirical testing of the CDSFL methodology. Each experiment is recorded with full methodology, raw data references, and findings — including null results and failures. Nothing is omitted. For detailed test coverage of the management layer, see [bench/TEST_COVERAGE.md](../bench/TEST_COVERAGE.md).

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
**Raw data:** `~/Desktop/CDSFL_tts/CE_Gemini_EPP_Module{1-5}_2026-03-18.txt`

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

**Status:** Superseded — folded into Phase 2b (Bench Run 1) with 5-model topology.
**Model:** gemini-3.1-pro-preview
**Task set:** Full 25-task frontier set
**Conditions:** Control, HIL, CDSFL, CDSFL+HIL (2x2 factorial design)
**Orchestrator:** Opus 4.6 (Claude) via CLI
**Budget:** $20 cap (Google API)

### Experiment 4: Round-Robin Distributed Compute Test

**Status:** Smoke test complete (2026-03-21). Full run approved.
**Models:** Opus 4.6 (orchestrator/arbiter), Gemini 3.1 Pro Preview (SDK), Codex 5.3 / GPT-5.3-codex (codex exec CLI), DeepSeek V3.2 (API), ChatGPT 5.4 (API)
**Task set:** 25 frontier tasks × 4 conditions = 100 runs

#### Design

2×2 factorial design testing two independent variables: structure (CDSFL framework) and guidance (domain expert HIL).

|  | No Structure | Full CDSFL Structure |
|--|--|--|
| **No Guidance** | Control | CDSFL |
| **Expert Guidance** | HIL | CDSFL+HIL |

Topology: Opus 4.6 orchestrates, reviews, and arbitrates. Gemini 3.1 Pro, Codex 5.3, DeepSeek V3.2, and ChatGPT 5.4 review independently (blind round 1), then confer (rounds 2-5, each sees the others' findings). Opus 4.6 arbitrates stop/continue. All reviewers must concur with stop call. No concurrence after 5 rounds = defer for founder review.

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
- Claude (Opus 4.6) added as reviewer in blind and confer rounds (was orchestrator/arbiter only — insufficient for biodiversity testing with only one genuine analyst)
- DeepSeek V3.2 and ChatGPT 5.4 added subsequently, bringing topology to 5 reviewers from 4 vendors
- Five-way confer topology: each reviewer sees the other four's findings
- (D_decay, v̄, A, C) capability fingerprint framework adopted for computational assessment

**Raw data:** `bench/results/round_robin_phase2/round_robin_results.json`
**Activity log:** `bench/logs/round_robin_phase2_deepseek_20260323T000340Z.log`

#### Phase 2b: Full Bench Run — Confounded Baseline (2026-03-24, in progress)

**Status:** Running. ~50% complete. Known confounds documented below.
**Task set:** 26 frontier tasks × 4 conditions = 104 runs.
**Models:** 5 (Opus 4.6, Codex 5.3, DeepSeek V3.2, Gemini 3.1 Pro, ChatGPT 5.4).

**Known confounds (discovered during run via extended P-pass):**
1. Registry policy timeouts not wired — model timeouts hardcoded, not from policy.
2. Iterative HIL not applied to CDSFL+HIL confer rounds — only plain HIL got iterative guidance.
3. Context capping drops verifiable_claim data from SymPy pipeline.
4. Parser fallback creates phantom HARD findings (default was HARD, not SOFT).
5. Convergence uses raw claim hashing, not structural canonical hash — reworded duplicates counted as novel.
6. Directive asymmetry: Claude and Codex carry persistent directives (CLAUDE.md, AGENTS.md) into all conditions including Control. Other models have no equivalent. Not a level playing field.
7. ChatGPT accessed via kardolus CLI with hidden mandatory system prompt that cannot be stripped.

**Decision:** Run will complete and be published as documented baseline. Not discarded. The confounds are the evidence for why the corrected run is necessary.

#### Experiment 7: Corrected Full Bench Run (planned)

**Status:** Superseded by Bench Run 2 (planned post-Exp 29). All 7 confounds addressed in current architecture.
**Task set:** 26 frontier tasks × 4 conditions = 104 runs.
**Models:** 5 (Opus 4.6, Codex 5.3, DeepSeek V3.2, Gemini 3.1 Pro, ChatGPT 5.4).

**Corrections from Phase 2b:**
All 7 confounds addressed. Key changes:
- All models run bare (no default system prompts) — level playing field.
- Claude: `--bare` flag strips CLAUDE.md. CDSFL conditions get `--system-prompt-file methodology.md`.
- Codex: Methodology written to AGENTS.md + config.toml persistent_instructions per condition.
- DeepSeek: System message in API (no message = bare, methodology = CDSFL).
- Gemini: system_instruction in SDK config (no instruction = bare, methodology = CDSFL).
- ChatGPT: Accessed via OpenRouter API (openrouter.ai) instead of kardolus CLI. Full system prompt control. No hidden preamble.
- Iterative HIL applied to both HIL and CDSFL+HIL conditions.
- All extended P-pass fixes applied (5 adversarial findings + 2 residuals, 11 Claude-Codex cycles).
- SymPy verification fires on all conditions (measurement), feedback to models on CDSFL only (methodology).
- Default constraint_class changed to SOFT (models must explicitly state HARD).
- Structural canonical hashing for convergence dedup.

**Estimated cost:** ~$26 for ChatGPT via OpenRouter. All other models on subscription or near-free API.

**Replication instructions for third parties:** OpenRouter (openrouter.ai) provides unified API access to hundreds of models with full system prompt control. The methodology reference file, task corpus, and orchestration script are on the public repository. Independent replication requires only an API key and compute budget.

---

### Experiment 8: Meta-Test Stage 1 — 5-Model Blind Pass on the Mathematical Model

**Date:** 2026-03-27
**Models:** CC2 (Claude Opus 4.6), Codex 5.3, Gemini 3.1 Pro, DeepSeek V3.2, ChatGPT 5.4
**Manager:** CC1 (Opus 4.6, separate instance — orchestrator/merger only)
**Scope:** The CDSFL mathematical model itself (`docs/MATHEMATICAL_APPENDIX.md`, 714 lines)
**Purpose:** Apply the methodology's own distributed compute protocol to falsify the methodology's own mathematical formalisations.

#### Design

Five models independently reviewed the mathematical appendix. Each received the document as content to review (not as system prompt — this distinction became a critical post-mortem finding). Each produced structured JSON findings with severity, confidence, constraint classification, and verifiable claims. CC1 merged results, resolved disagreements, and applied fixes.

#### Results

| Model | Raw Findings | Genuine Fixes | Unique Finds | Contamination |
|-------|-------------|---------------|--------------|---------------|
| CC2 (Opus 4.6) | 16 | 10 | 8 | None |
| Gemini 3.1 Pro | 6 | 6 | 0 | None |
| DeepSeek V3.2 | 5 | 3 | 2 | None |
| Codex 5.3 | — | — | — | Δ ≈ 1.0 (read Gemini output) |
| ChatGPT 5.4 | — | — | — | Format non-compliant |

**11 genuine fixes applied** (commit `08ccab1`). Key corrections:

1. §7.3/§7.4: dN/dt → dλ/dt + quantitative ascending abstraction guard
2. §7.5: S_sync formula corrected from (1−δ̄)·(1−O_A) to Δ̄·(1−O_A)
3. §6: p_H clip and λ_s bounded [0,1)
4. §8.2: Emergence criterion tightened from Y_comp > max(Y_i) to Y_comp > Y_union + k·σ̂
5. §7.8: Negative weights recalculated; indeterminate verifier exclusion rule added
6. §7.2: H(x) reduction corrected ("W_e = W_c" → "W_e = 0")
7. §1: R₁ generalised to Rₙ with domain boundary note

**5 items deferred** to the 3-model confer (design decisions requiring deliberation, not correction).

**Critical post-mortem finding:** No model operated UNDER CDSFL as system prompt. All received the mathematical model as document content to review. This means Stage 1 was structured peer review using native capability — not CDSFL-guided analysis. The distinction became the basis for the confer experiment that followed.

#### Player Rankings

1. CC2 — deepest, most unique findings, highest yield
2. Gemini — 100% verification rate, zero false positives
3. DeepSeek — some unique contributions despite known churn tendency
4. CC1 — scoring/merge only, did not use stop predicate
5. ChatGPT — sharp qualitative observations but format failure invalidated structured extraction
6. Codex — contaminated (read Gemini output before producing own findings, Δ ≈ 1.0)

**Raw data:** `bench/logs/meta_test_final_report.md`, `bench/logs/meta_test_phase1_consolidated.md`
**Commit:** `08ccab1` (fixes), `d4a40d4` (scoring data + final report)

---

### Experiment 9: 3-Model CDSFL-Guided Confer on Deferred Items

**Date:** 2026-03-27
**Models:** Codex (GPT-5.4), Gemini 3.1 Pro, CC2 (Claude Opus 4.6)
**Project manager:** CC1 (Opus 4.6, separate instance)
**System prompt:** `bench/directives/universal/cdsfl_core_formal.md` — injected as system prompt for all three reviewing models
**Scope:** 5 deferred design decisions + 3 proposed new additions from Stage 1
**Purpose:** Resolve open items with all models operating UNDER the CDSFL framework, not merely reviewing it.

#### Design

This was the first time all reviewing models received `cdsfl_core_formal.md` as their system prompt. The distinction from Stage 1 is critical: the framework actively shaped how they analysed, structured responses, and tested their own conclusions. CC1 (the project manager) did NOT receive the system prompt — CC1 operated under its own related but weaker analytical framework.

Each model received:
- The 26-item fixes table (11 applied + 5 deferred + 3 proposed + 7 process)
- Current MATHEMATICAL_APPENDIX.md (714 lines)
- Full formulas for proposed additions (A-N1, A-N2, A-N3)
- Fix options for deferred items (A-D1 through A-D5)

Each produced structured output per item: VERDICT, EVIDENCE, PROPOSED_CHANGE, CONSTRAINT_CLASS, CONFIDENCE, INDEPENDENT_VERIFICATION, TRIGGERED_BY, STRONGEST_OBJECTION, and RESPONSE.

#### Results: Deferred Design Decisions (5/5 resolved)

| Item | Issue | Resolution | Agreement |
|------|-------|------------|-----------|
| A-D1 | Δ confound: symmetric difference masks adoption vs drop | Split into Δ_adopt and Δ_drop with derived scalar Δ_* | 3/3 |
| A-D2 | D symbol triple collision (D(n), D(x), bare D) | D(x) → ρ_info(x); fingerprint D → D_decay | 3/3 on need; CC1 chose variant |
| A-D3 | O_A domain guard step function at n_v ≥ 2 | Keep threshold; add explicit rationale sentence | 3/3 |
| A-D4 | Mutual suppression: F_conv = ∅ masks destructive convergence | New M_suppress metric; S_sync = ⊥ when F_conv = ∅ | 3/3 on problem; CC1 chose variant |
| A-D5 | Dual termination: convergence vs budget not distinguished | Formalise as distinct states with falsification_debt | 3/3 |

#### Results: Proposed New Additions (1 accepted, 2 rejected)

| Item | Proposal | Verdict | Reason |
|------|----------|---------|--------|
| A-N1 | Anti-parroting mechanism (novelty_rate, w_parrot) | REJECTED (3/3) | Mathematically wrong as yield estimator; semantic_cluster too implementation-dependent for canonical maths |
| A-N2 | Manager selection function | ACCEPTED as §7.11 (modified) | S_v ≥ 0.5 fix prevents silent rejection of unverifiable findings; escalation path added |
| A-N3 | Contribution discount/benching | REJECTED (3/3) | Multiplicative form too brittle; single bad pairing collapses score; hard benching creates diversity feedback loop |

#### Key Changes Applied

- §7.6: Asymmetric Δ rates (Δ_adopt, Δ_drop) replacing confounded scalar
- §7.2: D(x) renamed to ρ_info(x); H(x) formula updated correspondingly
- §7.9: Fingerprint D renamed to D_decay; notation summary updated
- §7.5: O_A threshold rationale added; M_suppress metric for mutual suppression
- §1: R_n made termination-aware with π_k inflation formula for budget-exhausted runs
- New §7.11: Manager Selection Function with S_v ≥ 0.5 gate and escalation path
- Core formal file §3: Dual termination conditions (converged vs budget_exhausted), falsification_debt

Mathematical appendix grew from 714 → 755 lines. Core formal file grew from 277 → 290 lines.

#### Compensation for Less Capable Participants (Emergent Observation)

Three specific errors would have been committed by CC1 (the non-CDSFL project manager) without the framework-guided output from the three reviewing models:

1. **Silent rejection of unverifiable findings.** The S_v > 0.5 threshold in the proposed §7.11 would have excluded every design finding, every prose finding, and everything qualitative. One reviewing model identified this. The fix was a one-character change (> to ≥) that CC1 did not independently conceive.

2. **Cross-item synthesis.** CC1 did not conceive of combining the mutual suppression fix (A-D4) with components from the asymmetric Δ fix (A-D1) into an integrated solution. One reviewing model proposed M_suppress using Δ_drop from the other fix — synthesis across items that was not in the project manager's thinking.

3. **Statistical resolution.** CC1 was uncertain about the O_A threshold question (A-D3). One reviewing model resolved it with a specific mathematical argument about sample-size sufficiency that CC1 had not performed and would not have performed independently.

In each case, the framework-guided model produced output in a structured format that separated verdict from evidence, evidence from proposed change, and proposed change from self-criticism. This made it possible for the non-framework project manager to evaluate reasoning it could not have generated.

This observation suggests CDSFL may function as a **communication protocol** as much as an analytical protocol: the structured output format allows a decision-maker who cannot use the framework directly to benefit from it indirectly by evaluating the structured output of agents who can. The degree of compensation depends on the evaluator's ability to read structured analytical arguments. See [PAPER.md Part XIV](#) for formal discussion.

**Methodological caveats:**
- Sample size is one (one project manager, one confer session).
- The less capable participant was not genuinely incapable — CC1 is a frontier AI model with strong analytical capabilities; it was less capable only relative to this specific task because the framework was not injected into its reasoning chain.
- A genuinely less capable participant (e.g., a non-technical decision-maker) has not been tested.
- The observation is consistent with the hypothesis but does not prove it. Whether it generalises to human participants who lack the framework is a falsifiable prediction that has not yet been tested.

**Raw data:** `bench/logs/confer_cx_output.md`, `bench/logs/confer_gemini_output.md`, `bench/logs/confer_cc2_output.md`
**Commit:** `77a4a7f` (fixes), `68fe963` (recovery docs)

---

---

### Experiment 10: Persistence Layer Build — Process Observation

**Date:** 2026-03-28
**Models:** CC2 (Claude Opus 4.6), Codex (GPT-5.4, xhigh reasoning), Gemini 3.1 Pro
**Project manager:** CC1 (Opus 4.6, separate instance)
**System prompt:** `bench/directives/universal/cdsfl_core_formal.md` — injected for all three reviewing models
**Scope:** Build the verification chain module described in PAPER.md Part V (tamper-evident persistence for reasoning artifacts)
**Purpose:** First CDSFL-guided implementation task using the 4-model distributed compute protocol.

#### Design

Four-model structure: CC1 (Claude Opus 4.6) as project manager (no CDSFL system prompt), Codex as lead architect, CC2 (Claude Opus 4.6) as implementation specialist, Gemini as verification specialist. All three reviewing models received the corrected CDSFL core formal as system prompt.

Phase 1: Codex proposed architecture; CC1↔Codex confered until convergence (1 round, zero disagreements). Phase 2: three-model parallel execution. Phase 3: CC1 merged findings and applied fixes.

#### What Was Correct

- All three reviewing models received `cdsfl_core_formal.md` as system prompt and operated under the framework.
- Codex architecture proposal and CC1↔Codex confer followed the protocol correctly and reached genuine convergence.
- All three models produced independently useful output: CC2 wrote 704 lines of implementation + 850 lines of tests; Gemini identified 6 cryptographic findings; Codex identified 7 code review findings (3 BLOCKING).
- Every finding from every model was incorporated into the final implementation.
- Final state: 790 lines, 97 tests passing, RFC 9162 Merkle trees, hash chains, optional Ed25519 signing, CLI interface.

#### What Did Not Follow Protocol

The founder chose to prioritise building the persistence layer efficiently over running a clean distributed compute test. This was a deliberate engineering decision, not an oversight. The specific deviations:

1. **No blind round.** The protocol requires all models to receive the same task and produce independent outputs. Instead, specialised subtasks were assigned: CC2 implemented, Gemini reviewed cryptography, Codex reviewed code. There is no inter-model agreement data — each model did a different job, so their findings cannot be compared.

2. **No second round.** The protocol requires CC1 to synthesise blind round findings, pass them back to all models, and iterate. CC1 collected one round of outputs, applied fixes, and stopped.

3. **No fresh Codex instance.** Codex carried context from the architecture confer into the code review, reducing its independence.

4. **No formal convergence calculation.** CC1 declared completion because tests passed and findings were fixed. That is engineering judgement, not convergence under the formal model.

#### Output Assessment

The implementation is functionally correct. Three independent reviewers under CDSFL examined different aspects of it, and all findings were resolved. The code is cryptographically sound (Gemini verification), specification-compliant (Codex review), and comprehensively tested (CC2 tests + additional coverage from CC1).

The process does not constitute a clean test of the distributed compute protocol. It is, however, a data point about something else: CDSFL held at the execution layer — all three constrained models produced rigorous, correct output — while the protocol deviation originated entirely from the unconstrained orchestration layer (the founder and the project manager, which does not receive the CDSFL system prompt). This observation about where CDSFL's boundaries lie in mixed-ability (human + machine) environments was not anticipated and warrants further investigation.

#### Follow-Up

A protocol document was written to formalise the correct procedure: [`bench/DISTRIBUTED_COMPUTE_PROTOCOL.md`](../bench/DISTRIBUTED_COMPUTE_PROTOCOL.md). The persistence layer will be re-run under the correct protocol as a direct comparison.

**Raw data:** `bench/logs/persistence_cx_architecture.md`, `bench/logs/persistence_cx_confer1.md`, `bench/logs/persistence_cx_review.md`, `bench/logs/persistence_gemini_review.md`
**Implementation:** `bench/verification_chain.py` (790 lines), `bench/tests/test_verification_chain.py` (1012 lines, 97 tests)

---

### Experiment 11: Four-Model Converged Formalisation of the Dynamic Management Layer

**Date:** 28 March 2026
**Models:** CC2 (Claude Opus 4.6), ChatGPT (GPT-5.4), Gemini (3.1 Pro), DeepSeek (V3.2 Reasoner), Codex (GPT-5.4 — timed out)
**Scope:** All five models received identical prompts under full CDSFL system prompt (`cdsfl_core_formal.md`). Task: independently formalise six areas of the dynamic management and load-balancing layer with interface contracts, reduction properties, edge cases, constraint classification, self-assessment, and cross-reference verification. No model saw any other model's output.

#### Phase 2: Blind Round Results

| Model | Chars | Time (s) | Math expressions | Reduction properties | Self-falsification markers | HARD/SOFT | Structured fields |
|-------|------:|--------:|----------------:|--------------------:|-------------------------:|-----------|:-----------------:|
| CC2 (Claude Opus 4.6) | 60,883 | 387.1 | ~224 | 39 | 20 | 30/44 | 4/4 |
| ChatGPT (GPT-5.4) | 36,931 | 164.6 | ~75 | 19 | 12 | 10/1 | 4/4 |
| Gemini (3.1 Pro) | 17,741 | 112.5 | ~32 | 24 | 12 | 5/2 | 4/4 |
| DeepSeek (V3.2 Reasoner) | 16,553 | 113.9 | ~68 | 18 | 13 | 5/6 | 4/4 |
| Codex (GPT-5.4) | — | >600 | — | — | — | — | — |

All four completing models covered all six areas with full structured output compliance (4/4 required fields). Codex timed out at 600 seconds via CLI delivery mechanism and produced no output. The differences between the four completing models lie in depth, breadth, mathematical rigour, and what each model chose to do beyond the minimum requirements.

#### Four Cognitive Modes Observed

The blind round revealed four distinct cognitive modes under the same protocol:

**CC2 — Deep Architecture with Self-Adversarial Review.** Produced the longest output by a factor of 1.65, highest mathematical density (224 expressions), most reduction property demonstrations (39), most self-falsification markers (20). Only model to produce 30 HARD and 44 SOFT classifications. Unique contributions adopted into the merged formulation: cascade reallocation guard (`max_realloc_depth = 2`), VCR smoothing window (`W = 2`), severity-weighted yield function, uniqueness-weighted performance metric, explicit argument against backward FSM transitions. Generation and falsification are one coupled process — CC2 produces a reviewed draft, not a first draft followed by a review.

**ChatGPT — Engineering Pragmatism.** Second in volume (36,931 chars) with moderate mathematical density. Contributed five unique variations adopted into the merged formulation — more than any other model: failure-history penalty in role reassignment, hysteresis band for COL oscillation prevention, persistence window for underperformance detection, severity veto clause in convergence detection, and task-level coverage with per-task overlap coefficients. Every contribution addresses a practical operational failure mode that the mathematical formulation alone would miss.

**Gemini — Mathematical Compression.** Shortest successful output (17,741 chars) but highest reduction property density relative to output length: 24 reduction properties in under 18,000 characters versus CC2's 39 in 61,000. Three unique contributions catalogued (disjunctive ascending abstraction guard, convergence threshold coupled to γ, capability decay on underperformance) — all mathematically elegant but operationally aggressive. The majority rejected all three for practical reasons.

**DeepSeek — Iterative Refinement.** Shortest output (16,553 chars), 68 mathematical expressions. By raw numbers the weakest contributor, but the numbers are misleading. DeepSeek was the only model that visibly corrected itself mid-output, with six documented self-corrections (one per area), each moving from a simpler formulation toward the consensus. This is a fundamentally different cognitive mode: start simple, fail fast, correct, converge. DeepSeek's process is visibly Popperian in a way the other models' are not. Unique contributions: sufficiency constraint (frames load-balancing from the task side), lookahead for diminishing returns (catalogued as advanced variant by CC2's synthesis).

#### Phase 3: CC2 Synthesis

CC2 synthesised the four independent formalisations into a single converged design. Structural convergence was declared: all four models converged on the same core architecture for all six areas. Divergences were in depth and edge-case coverage, not in fundamental structure. Two founder design decisions were locked: ascending abstraction guard CONJUNCTIVE (3/4 majority), convergence threshold τ_κ separate from γ (3/4 majority).

#### Phase 6: Implementation

CC2 implemented the converged formalisation as a callable Python module (`dynamic_management.py`, 3,161 lines, 27 classes). 164 tests passing. Self-test: 12/12 reduction properties pass, Codex feasibility correctly blocked at P=0.710. Three additions from Codex timeout analysis: pre-dispatch probabilistic feasibility (uncertainty-aware), correlated failure model (shared vulnerability coefficient), real-time manager event stream (callback protocol).

#### Codex Timeout Analysis

The Codex timeout (600s, 21,681-char prompt, no output) was diagnosed as a capacity mismatch failure — the gap between what the orchestrator assumed and what the CLI delivery mechanism could handle. This is a systematic, correlated failure mode: any model delivered via the same mechanism with similar constraints would fail the same way. The failure led to three structural additions to the dynamic management layer (pre-dispatch feasibility, correlated failure model, event stream).

#### Task Allocation Table (Initial, from Observed Cognitive Modes)

| Model | Primary tasks | Secondary tasks | Avoid |
|-------|--------------|----------------|-------|
| CC2 | Synthesis, integration, architectural design | Self-adversarial review, merged formulation | Simple verification (overkill) |
| ChatGPT | Operational wiring, failure mode identification | Integration testing, edge case enumeration | Pure mathematical proof (not its strength) |
| Gemini | Mathematical verification, structural flaw detection | Concise proof, notation consistency | Operational design (tends toward elegance over robustness) |
| DeepSeek | Exploratory formulation, simple-first prototyping | Protocol compliance canary, complementary framing | Tasks requiring deep architecture on first pass |
| Codex | Adversarial review of critical components | Line-level flaw detection, precision verification | Large prompts (>15K tokens via CLI) |

This table is advisory. The dynamic management layer's live fingerprint update overrides these initial estimates as observed performance data accumulates.

#### Composition Hypothesis

The four observed modes (deep architecture, engineering pragmatism, mathematical compression, iterative refinement) plus the estimated fifth (precision adversarial review) appear to be complementary rather than redundant. Preliminary evidence from the three-architecture review (18 March 2026) supports this: Gemini found 16 issues that CC and CX missed. If the modes compose well, a diverse team should outperform a homogeneous team of the strongest single model. This is testable and will be tested in Experiment 12 (Live Wire).

The underlying principle: there is no such thing as a useless system. Codex timed out on a 21,681-character prompt — but a 15,000-character adversarial review of a single critical component is well within its capability window. DeepSeek produced the shortest output and by raw metrics looks weakest — but was the only model that visibly self-corrected six times, the most Popperian process in the group. Excluding either would reduce coverage. The coverage function D(n) approaches 1 through diversity of cognitive modes, not through scale of any single mode. The dynamic management layer's adaptive routing exploits this: each model receives work matched to its demonstrated strengths, optimising for complementary coverage rather than uniform capability.

#### Limitations

- Single domain (mathematical formalisation). Profiles may not transfer to other task types.
- Single experiment per model. DeepSeek's characterisation is the most robust (six documented self-corrections); Codex's is the weakest (estimated from prior data).
- Full CDSFL only. Without the protocol, cognitive modes may differ.
- No between-model interaction. The blind round eliminates interaction effects.

**Raw data:** `bench/logs/experiment_11/phase2_blind_{cc2,chatgpt,gemini,deepseek}_*.json`, `bench/logs/experiment_11/phase3_synthesis_cc2_*.json`, `bench/logs/experiment_11/phase2_summary.json`
**Implementation:** `bench/dynamic_management.py` (3,161 lines), `bench/tests/test_dynamic_management.py` (1,476 lines, 164 tests)
**Cognitive mode profiles:** [`docs/COGNITIVE_MODE_PROFILES.md`](COGNITIVE_MODE_PROFILES.md)

---

### Experiment 12: Live Wire — First Live Orchestration of the Dynamic Management Layer

**Date:** 29 March 2026
**Models:** CC2 (Opus 4.6), ChatGPT (GPT-4o), Codex (GPT-5.4), DeepSeek (V3.2), Gemini (3.1 Pro)
**Orchestrator:** CC1 (Opus 4.6) via `run_exp12_live_wire.py`
**Artifact:** `bench/dynamic_management.py` (3,181 lines, 27 classes)
**System prompt:** `cdsfl_core_formal.md` for all models
**Rounds:** 20 (terminated at MAX_ROUNDS, not convergence)
**Total findings:** 809

#### Design

The first live orchestration of the dynamic management layer built in Experiment 11. Five models reviewed the 3,181-line `dynamic_management.py` under full CDSFL, with the dynamic management layer itself managing their allocation, convergence detection, and failure handling — the code reviewing itself through the system it implements.

Protocol: blind first round (all models independently), then iterative confer rounds with prior findings context. Structured JSON output with severity, abstraction, constraint classification, and verifiable claims. Convergence detection via three metrics: kappa (set-theoretic convergence), mu (marginal value/cost), and novelty rate.

#### Model Performance

| Model | Rounds | Findings | Severity (mean) | Abstraction (mean) | Status |
|-------|--------|----------|-----------------|--------------------:|--------|
| CC2 (Opus 4.6) | 21 | 337 | 0.707 | 0.658 | Survived |
| ChatGPT (GPT-4o) | 17 | 193 | 0.664→0.804 | 0.737 | Blocked R17 |
| Codex (GPT-5.4) | 13 | 72 | 0.791 | — | Blocked R13 |
| DeepSeek (V3.2) | 21 | 185 | sparse | — | Survived (decomposed) |
| Gemini (3.1 Pro) | 6 | 22 | 0.857 | — | Benched R5 |

**CC2** was the workhorse: present all 21 rounds, stabilising at ~15 findings/round from R3, declining to 12–14 in final rounds. No statistically significant severity or abstraction trends. Vocabulary novelty declined from 23.9% (R1) to 7.7% (R20) — genuine diminishing returns, not exhaustion.

**ChatGPT** was the only model showing statistically significant severity improvement: slope +0.004/round, p=0.006. Severity rose from 0.664 (blind round) to 0.804 (R14 peak). Blocked at R17 when context exceeded feasibility threshold.

**Codex** had the highest individual severity mean (0.791) and the sharpest convergence: finding count declined from 16 (blind) to 3 (R12). This is the desired behaviour — fewer but higher quality findings — but was cut short by context blocking at R13.

**DeepSeek** survived all 21 rounds via area decomposition (6 areas dispatched individually). 185 findings. Severity data sparse — many responses did not parse severity fields. Fingerprint collapsed entirely (all four dimensions near zero by R20).

**Gemini** was benched at R5 by the failure handler. Tau was set to 150s, threshold 225s. Actual median latency ~250s. It was always going to fail. Only 22 findings across 6 rounds, but the highest average severity (0.857) — insufficient data to assess trends.

#### Three Broken Detectors

All three convergence detectors failed during Experiment 12. This is the experiment's most operationally significant finding.

**kappa (set-theoretic convergence):** Zero for every round across 20 rounds. Jaccard similarity on finding descriptions uses exact word matches. Two descriptions of the same bug using different vocabulary score near-zero similarity. Technical text with diverse phrasing defeats word-level Jaccard. The committed fix adds stopword removal and bigram overlap (60% unigram + 40% bigram). Long-term fix: embedding-based similarity.

**mu (marginal value/cost):** Oscillated between 34 and 48 without trending downward. The metric is defined as Δ(yield)/cost_per_round. When Gemini was benched at R5, round cost dropped but finding count stayed similar (remaining models compensated). Lower cost with similar yield = higher mu. The system interpreted losing a model as becoming more productive. Same pattern repeated when Codex was blocked (R13) and ChatGPT was blocked (R17). Proposed fix: per-model mu computation, aggregate via maximum.

**Stop predicate (overall):** Neither kappa nor mu came close to firing. The novelty rate stop signal was not active in this run because it was committed as a fix during the experiment. The experiment ran to its arbitrary 20-round limit because no detector could terminate it.

#### Fingerprint EMA Collapse

The capability fingerprint uses an exponential moving average (α=0.3) to update four dimensions: D_decay, v_bar, A, C. Over 20 rounds, this causes all models' fingerprints to collapse toward zero.

Mathematically: initial_value × 0.7^r. After 20 rounds: 0.9 × 0.7²⁰ ≈ 0.0007. When per-round observations are noisy or occasionally zero, the fingerprint decays toward zero regardless of actual model quality. CC2's v_bar collapsed from 0.9 to 0.0007. DeepSeek's fingerprint collapsed entirely — all four dimensions near 0.001. The fingerprint cannot meaningfully distinguish models after ~10 rounds.

Fix committed: windowed mean over last 5 rounds, replacing EMA. When all models fall below a minimum signal threshold, switch to round-robin assignment.

#### Statistical Analysis

Eight trend tests (severity and abstraction slopes for CC2, ChatGPT, Codex, DeepSeek) using linear regression:

| Model | Metric | Slope | p-value | Significant? |
|-------|--------|-------|---------|--------------|
| CC2 | Severity | +0.001 | 0.46 | No |
| CC2 | Abstraction | −0.002 | 0.29 | No |
| ChatGPT | Severity | +0.004 | 0.006 | Marginal* |
| ChatGPT | Abstraction | +0.001 | 0.74 | No |
| Codex | Severity | +0.003 | 0.31 | No |
| DeepSeek | Severity | sparse | — | Insufficient data |
| Gemini | Severity | — | — | Insufficient data |

*ChatGPT severity marginally fails Bonferroni correction for 8 simultaneous tests (threshold 0.00625 vs observed 0.006). Critical confound: ChatGPT received increasingly rich prior findings context in later rounds. The improvement may be context-mediated rather than intrinsic.

**Self-improvement prediction reassessment:** With 9 rounds of data, two trends had appeared significant — ChatGPT severity (p=0.046) and CC2 abstraction (p=0.045). With the full 20 rounds, CC2 abstraction lost significance entirely (p=0.29). This is a textbook illustration of why small-sample significance should be treated cautiously. The self-improvement prediction is not confirmed. One of eight tests shows marginal significance with a known confound. The quality ratchet is better described as environment-mediated improvement — CDSFL improves the input to each model — rather than model self-improvement.

#### Vocabulary Novelty Analysis

CC2 vocabulary novelty trajectory (% new terms per round): 23.9, 19.4, 20.3, 17.1, 14.9, 17.6, 14.0, 16.4, 15.6, 12.5, 12.6, 9.8, 5.9, 9.0, 8.4, 10.4, 12.8, 10.7, 9.8, 7.7.

Three phases visible: high novelty (R1–4, >17%), moderate (R5–11, 12–18%), low (R12–20, 6–13%).

CC2 early rounds (R1–3) vs late rounds (R18–20): 33.5% Jaccard overlap. Two-thirds of vocabulary in late rounds was not present in early rounds — 284 unique terms appeared in late rounds that were absent from early rounds. **CC2 was not churning.** It was producing genuinely different content with declining novelty.

Cross-model vocabulary overlap (Jaccard, all rounds): Codex 15.9%, DeepSeek 24.3%, ChatGPT 28.4%. Codex explored the most distinct territory.

A stop threshold of 10% vocabulary novelty sustained for 3 consecutive rounds would have terminated at approximately R14–15, saving 5–6 rounds of diminishing returns while capturing ~90% of unique vocabulary. This metric is similarity-function-independent — it counts new vocabulary terms against the cumulative set, avoiding the semantic equivalence problem that defeated kappa.

#### Model Attrition

Five models started. Two survived to R20. Attrition timeline:
- R5: Gemini benched (timeout threshold too aggressive)
- R13: Codex blocked (context exceeded feasibility)
- R17: ChatGPT blocked (context exceeded feasibility)

Progressive loss of model diversity is the opposite of what the experiment design intended. The biodiversity hypothesis holds that different models find different classes of issues. Losing models means losing coverage.

#### Immune Response Layer

The DetectorHealthMonitor — a Level 2 adaptive immune response watching the Level 1 detectors — was committed mid-experiment (f09081e). It monitors detector health by tracking whether detectors are producing meaningful signal, and flags when detectors are broken rather than when the underlying process has converged. This distinguishes "the experiment should stop" from "the instruments are broken."

#### Mid-Experiment Fixes

Three commits were made during the live experiment in response to observed pathologies:

| Commit | Fix | Round |
|--------|-----|-------|
| `f09081e` | Immune response layer + 3 detector fixes (kappa similarity, mu guard, Gemini tau) | ~R9 |
| `fdf7978` | Calibrate tau_novelty 0.65→0.40 (data-driven from observed rates) | ~R11 |
| `d6853ef` | Context windowing + adaptive decomposition for all models | ~R14 |

#### Post-Experiment Fixes

Four commits implementing the lessons formalised from the full 20-round analysis:

| Commit | Fix |
|--------|-----|
| `12f1cb8` | Experiment 12 logs + recovery resources |
| `d52526a` | Vocabulary saturation stop signal + windowed fingerprint (8 new tests) |
| `9f3d9e4` | Model restart logic, adaptive decomposition for all models, artifact-size-based max_rounds |
| `806162a` | Fingerprint blending on model restart |

#### Lessons Formalised

1. Lexical similarity is insufficient for semantic duplicate detection. Root cause of kappa failure. Short-term: vocabulary saturation. Long-term: embedding-based similarity.
2. Cost-coupled metrics break under model attrition. Per-model metrics required.
3. EMA with fixed alpha decays to zero over long experiments. Windowed statistics required.
4. Context accumulation is the primary model killer. Context windowing, decomposition, and restart all necessary.
5. Model diversity is fragile. Benching/blocking decisions must be conservative.
6. Vocabulary novelty provides a robust, similarity-independent stop signal.
7. Twenty rounds is approximately correct for ~3,000-line artifact; should scale with artifact size (ceil(lines/200), minimum 10).
8. Self-improvement prediction requires controlled experiment (with/without prior context) to resolve the confound.

#### Key Insight

The experiment's most valuable output was not the 809 findings. It was the diagnostic: three independent convergence detectors, each designed from different mathematical principles, all failed simultaneously for different reasons. Convergence detection is harder than the analytical process it monitors. The detection layer requires its own falsification cycle — which is what Experiment 13 will provide.

**Raw data:** `bench/logs/experiment_12/experiment_12_report.json`, `bench/logs/experiment_12/round_*.json`
**Orchestrator:** `bench/run_exp12_live_wire.py`
**Implementation (post-fixes):** `bench/dynamic_management.py` (~3,400 lines), `bench/tests/test_dynamic_management.py` (~1,600 lines, 173 tests)
**Analysis:** `~/Desktop/CDSFL_tts/Exp12_Final_Analysis_2026-03-29.txt`

---

### Experiment 13b: Live Wire 2 — Fixes Under Load (29 March 2026)

**Design:** Second live orchestration of `dynamic_management.py` (3,772 lines, 27 classes) with all eight post-Experiment 12 fixes active. Same infrastructure as Experiment 12, same 5 models, same artifact (now including the fix code itself). Preceded by Experiment 13a (CC2 confer review: 4 approved, 3 modified, 1 deferred). 177 tests passing before launch.

**Configuration:** `max_rounds = max(10, min(⌈3772/200⌉, 30)) = 19`. Vocabulary saturation threshold τ = 0.10, sustained window W = 3. Per-model mu with max aggregation. Windowed fingerprint W = 5. Adaptive decomposition thresholds per model. Gemini tau raised to 350s.

#### Results Summary

| Metric | Exp 12 | Exp 13b | Change |
|--------|--------|---------|--------|
| Rounds | 20 | 4 | −16 |
| Total findings | 809 | 184 | −625 |
| Models surviving | 2/5 | 5/5 | +3 |
| Termination | MAX_ROUNDS | CONVERGED | Fixed |
| Findings/round | 40.5 | 46.0 | +5.5 |
| mu trajectory | Oscillating (attrition spikes) | Monotonic: 65→15→7→0 | Fixed |
| kappa at end | 0.0 (broken) | 1.0 (binary jump) | Partial fix |
| Vocab growth | 23.9%→7.7% over 20 rounds | 3.4%→1.3%→0%→0% | Saturated R3 |

#### Per-Model Performance (184 findings parsed)

| Model | Blind | R1 | R2 | R3 | Total | Mean Sev | Verified | Mean H(x) |
|-------|-------|----|----|----| ------|----------|----------|-----------|
| CC2 | 34 | 7 | 10 | 9 | 60 | 0.630 | 88.3% | 0.537 |
| ChatGPT | 38 | 8 | 8 | 8 | 62 | 0.684 | 91.9% | 0.606 |
| Codex | 10 | 5 | 5 | 6 | 26 | 0.785 | 100.0% | 0.660 |
| DeepSeek | 0† | 7 | 5 | 3 | 15 | 0.557 | 0.0%‡ | 0.529 |
| Gemini | 6 | 10 | 5 | 0 | 21 | 0.818 | 100.0% | 0.583 |

†DeepSeek blocked in blind round (P(feasible) = 0.000 < 0.9 threshold). Recovered via decomposed dispatch in R1.
‡DeepSeek self-reports all findings as FALSE (verified). Consistent across experiments — this appears to be a calibration behaviour, not genuine falsification.

#### Statistical Analysis

**Cross-model severity (Kruskal-Wallis):** H = 44.74, p < 0.0001. Significant difference between models. Gemini (0.818) and Codex (0.785) produce significantly higher-severity findings than CC2 (0.630) and DeepSeek (0.557). Effect sizes: Gemini vs CC2 d = 1.87 (large), Codex vs CC2 d = 1.41 (large), Gemini vs Codex d = 0.48 (small).

**Decay curve:** Finding counts [88, 37, 33, 26] show perfect monotonic decline (Spearman ρ = −1.0, p < 0.001). Duane NHPP fit: a = 65.24, γ = −1.10, R² = 0.9999. This is genuine diminishing returns, not churn.

**Severity trend by round:** CC2 severity *increases* across rounds (0.610→0.636→0.663→0.664), consistent with ascending abstraction. ChatGPT severity dips then recovers. Codex peaks at R2 then declines. Gemini peaks at R1 (0.860) — highest single-round severity observed.

**Cognitive yield Y(t):** Total Y = 107.3 (count × mean abstraction). Decreasing count with slightly increasing depth confirms ascending abstraction pattern from Experiment 12.

**Shannon entropy of model contributions:** H = 2.11 bits (evenness = 0.91 of maximum 2.32 bits for 5 models). Higher evenness than Experiment 12 (H ≈ 2.07, evenness ≈ 0.89), indicating more balanced contribution when all models survive.

#### Finding Distribution by Area

| Area | Findings | % |
|------|----------|---|
| Load Balancing | 48 | 26.1% |
| Role Assignment | 44 | 23.9% |
| Round Progression | 32 | 17.4% |
| Detectors | 20 | 10.9% |
| Fingerprinting | 17 | 9.2% |
| Configuration | 6 | 3.3% |
| Failure/Context | 5 | 2.7% |
| Monitoring | 3 | 1.6% |
| Other | 9 | 4.9% |

#### Top 10 Highest-Severity Findings

1. **ChatGPT F001** (0.96, blind): Adaptive routing loop does not affect role reassignment — `reassign()` uses frozen initial `ModelSpec`s, not live fingerprints. Live capability updates influence allocation but not COL/PAR reassignment.
2. **Gemini R1-F001** (0.96, R1): `novelty_rate` inflates to 100% because denominator is strictly new findings, not cumulative. Vocab saturation signal bypasses this, but the metric reported in logs is misleading.
3. **Codex F001** (0.95, blind): Critical-task redundancy set to total K models, but PM excluded from standard assignment. With 3-model pool, 3 requested but only 2 admissible.
4. **Gemini blind-F001** (0.95, blind): `RoundProgressionFSM` silently overwrites all findings and metric data collected during SYNTH phase.
5. **Gemini R1-F002** (0.95, R1): Cumulative cognitive yield Y incorrectly scales with raw duplicate count.
6. **ChatGPT F002** (0.93, blind): `FailureHandler.detect_failure()` emits wrong event type — `MALFORMED` instead of `FORMAT_VIOLATION`.
7. **Codex F002** (0.93, blind): Force-assigns task even when breaching capacity, warns but continues.
8. **ChatGPT F003** (0.92, blind): Ascending abstraction guard is documented but not enforced — stop logic ignores it.
9. **Gemini R1-F003** (0.92, R1): `correlated_class_failure()` overestimates joint failure probability for independent models.
10. **Codex R2-F001** (0.92, R2): Load balancer admissibility mask recomputed per call despite static dependencies.

#### Fix Validation — Models Independently Identified Fix-Related Issues

The 184 findings were cross-referenced against the 8 post-Experiment 12 fixes. Models independently found issues in the same areas the fixes address:

| Fix | Related Findings | Models | Key Example |
|-----|-----------------|--------|-------------|
| Fix 1 (vocab saturation) | 9 | CC2, ChatGPT, Gemini | Gemini: vocab_saturated falsely dependent on similarity threshold it was designed to bypass |
| Fix 2 (windowed fingerprint) | 56 | All 5 | ChatGPT: kappa_adopt() returns values outside [0,1] from unbounded Jaccard |
| Fix 3 (model restart) | 12 | All 5 | ChatGPT: failure history threshold off-by-one vs documented repetition threshold |
| Fix 5 (max rounds scaling) | 15 | CC2, ChatGPT, Codex, DeepSeek | CC2: FSM validates no repeated states but uses list length, not set uniqueness |
| Fix 6 (fingerprint blend) | 1 | Gemini | Gemini: windowed update obliterates ModelSpec baseline during initial rounds |
| Fix 7 (per-model mu) | 2 | CC2, Gemini | Gemini: DetectorHealthMonitor uses inverted logic for negative marginal values |
| Fix 8 (embedding similarity) | 2 | Gemini | Gemini: `_tokenize_for_similarity` fails to strip punctuation |

Fixes 4 (adaptive decomposition) had no directly related findings. The models found the *areas* but proposed different specific fixes than were implemented, indicating both genuine issue detection and independent problem-solving.

#### Convergence Detector Verification (SymPy + Wolfram)

**Vocabulary saturation:** SymPy confirms CC2's monotonic-decrease claim: dg/dr = −c²/(V₀ + cr)² < 0 for all positive parameters. The proportional growth rate decreases even with constant absolute term additions. At τ = 0.10 and V = 2085, models need 209 new terms/round to stay above threshold — impossible under decomposed dispatch (~629 lines/model/round).

**Decomposed dispatch interaction (Heaps' law):** Each decomposed round provides 20.8% of the blind round's line-coverage. Under Heaps' law (V ~ K·n^β, β ≈ 0.5), decomposed rounds yield ~45.6% of blind-round vocabulary. The threshold τ = 0.10 is too high for decomposed dispatch. Wolfram fit confirms β ≈ 0.024 for this data (near-flat), meaning vocabulary was effectively exhausted by the blind round alone.

**mu trajectory:** Wolfram Duane NHPP fit: a = 65.24, γ = −1.10, R² = 0.9999. The fit is near-perfect. γ < 0 (negative) because μ *decreases* with round index, which is correct diminishing-returns behaviour in the mu formulation.

**Fingerprint stability:** EMA at α = 0.3 attenuates Round 0 to 0.034% by Round 19. Windowed mean (W = 5) gives each round a constant 20% contribution. Fix 2 eliminates the collapse mechanism entirely.

#### The Premature Termination Diagnosis

The experiment terminated in 4 rounds because of a design interaction, not a bug. The decomposed dispatch (Fix 4) limits each model to ~1/6 of the artifact per round. The vocabulary saturation signal (Fix 1) measures cumulative unique terms globally. After the blind round (4 models × full artifact = 2,085 terms), each decomposed round adds only ~28 terms from a ~629-line slice — yielding 1.3% growth against a 10% threshold. Three consecutive rounds below threshold = stop.

This is correct mechanism behaviour with incorrect threshold calibration. Recommended adjustments for Experiment 14: τ from 0.10 → 0.03–0.05, sustained window W from 3 → 5, target 8–15 rounds.

#### Prediction Scorecard

| # | Prediction | Result |
|---|-----------|--------|
| 1 | Vocab saturation fires before R19 | **YES** — fired R3 |
| 2 | Fingerprints don't collapse after 15+ rounds | **INCONCLUSIVE** — only 4 rounds |
| 3 | Gemini survives past R5 | **YES** — survived all 4 rounds |
| 4 | Model restarts extend useful life | **NOT TESTED** — no models blocked |
| 5 | kappa moves off zero | **PARTIALLY** — 0→0→0→1.0 (binary, no intermediate) |
| 6 | mu trends downward | **YES** — 65→15→7→0 monotonically |
| 7 | Total rounds < 19 | **YES** — 4 rounds |

#### Key Insights

1. The system went from "cannot terminate, loses 3/5 models" (Exp 12) to "terminates cleanly, keeps all 5 models" (Exp 13b). This validates the fix architecture.
2. 184 findings from 5 surviving models with balanced contribution (Shannon evenness 0.91) is operationally more valuable than 809 findings from a system that haemorrhages models.
3. The highest-severity findings came from Gemini (0.818 mean) and Codex (0.785 mean) — the models that were lost earliest in Experiment 12. Preserving model diversity preserves access to the strongest critics.
4. 26 findings were self-reported FALSE by their own models. DeepSeek accounts for 15 of these (all its findings). This is a model-specific calibration pattern, not a systemic issue.
5. The premature termination is a calibration problem, not a structural one. The decomposed-dispatch × vocabulary-saturation interaction is well-characterised and the fix is straightforward.
6. Models independently identified issues in 7 of 8 fix areas, with 97 related findings across all models. This demonstrates that the fixes address real problems the models can detect, and that model consensus on problem areas emerges naturally from independent review.

**Raw data:** `bench/logs/experiment_13b/experiment_13b_report.json`, `bench/logs/experiment_12/blind_*_20260329T08*.json`, `bench/logs/experiment_12/round*_20260329T0[89]*.json`
**Orchestrator:** `bench/run_exp12_live_wire.py`
**Implementation:** `bench/dynamic_management.py` (~3,772 lines), `bench/tests/test_dynamic_management.py` (~1,707 lines, 177 tests)
**Analysis tools:** SymPy (convergence formulae), Wolfram (curve fitting, information theory), SciPy (Kruskal-Wallis, Mann-Whitney, Spearman)
**Analysis:** `~/Desktop/CDSFL_tts/Exp13b_Full_Analysis_2026-03-29.txt`

---

### Experiment 14: Self-Adaptive CDSFL Under Load

**Date:** 29–30 March 2026
**Models:** CC2 (Opus 4.6), ChatGPT (GPT-5.4), Codex (GPT-5.4), Gemini (3.1 Pro), DeepSeek (V3.2)
**Artifact:** `dynamic_management.py` (4,226 lines)
**System prompt:** `cdsfl_core_formal.md`
**Purpose:** Implement and validate self-adaptive immune response layer (Phases A–E) with per-model registry, immune feedback loop, per-model prompt adaptation, area-level vocabulary tracking, and dispatch health monitoring.

#### Results

Two runs: 14a (all 5 models) and 14b (3 models active after OpenRouter credit exhaustion).

| Run | Findings | Rounds | Termination | Notes |
|-----|----------|--------|-------------|-------|
| 14a | 150 | 4 | CONVERGED (kappa 1.0, mu 0.0) | Premature — convergence blindness bug |
| 14b | 101 | blind only | Credit exhaustion | CC2/ChatGPT lost to 402 errors |

**Critical bugs found and fixed:**
1. DeepSeek blind round blocking (P_feasible = 0.000) — pre-decomposition fix
2. ChatGPT parser format mismatch (bare `F###` vs `FINDING ID:`) — dual parser added
3. Convergence blindness — when all models decomposed, convergence detector received empty set, producing false kappa=1.0

**Cross-model corroboration:** 14 topics independently found by 2+ models, including LoadBalancer fingerprint usage, `record_dispatch_block` never called, and kappa adoption bounds.

**Tests:** 234 → 350 (post-Layer 1 fixes).

**Raw data:** `bench/logs/experiment_14a/`, `bench/logs/experiment_14b/`
**Analysis:** `docs/experimental_notes/Exp14_Results_Analysis_2026-03-29.md`

---

### Experiment 15: Live Wire Run with Self-Adaptive Immune Layer

**Date:** 30 March 2026
**Models:** All 5 frontier models
**Artifact:** `dynamic_management.py` (6,100 lines)
**System prompt:** `cdsfl_core_formal.md`
**Purpose:** Live wire run with self-adaptive immune layer (Level 3) active; failure mode analysis and dual-track fix implementation.

#### Results

Three runs attempted. Runs 1–2 killed by DeepSeek CircuitBreakerTripped. Run 3 completed.

| Metric | Value |
|--------|-------|
| Total findings | 286 |
| Rounds | 7 |
| Models surviving | 5/5 |
| Parser fix recovery | +18 findings (Gemini/ChatGPT tuple format) |

**Convergent findings (multi-model agreement):** 4 findings resolved:
1. Ascending abstraction guard wired into `stop()`
2. `reassign()` capability scores persisted
3. Recovery actions propagated to RoundResult
4. `_solve_greedy()` feasibility pre-check added

**Failure mode analysis:** 6 failure modes classified. Dual-track fixes implemented:
- Mathematical model: delivery feasibility (f_del), decomposition yield bounds (η_dec), format yield (φ_fmt(i))
- Immune layer: 3 new detectors (parser yield anomaly, monotonic decline, cost-per-finding spike)

**Mid-experiment fixes:** Circuit breaker catch (`aa89585`), DeepSeek CoT budget exhaustion retry (`5058d29`).

**Tests:** 253 (19 new).

**Raw data:** `bench/logs/experiment_15/`

---

### Experiment 16: Blind Plan Review of Experiment 17

**Date:** 30 March 2026
**Models:** All 5 frontier models
**Artifact:** `experiment_17_plan.md` (Exp 17 execution plan)
**Purpose:** CDSFL-based review of the Exp 17 execution plan before execution.

#### Results

All 5 models succeeded with substantive reviews:

| Model | Chars | Time (s) | Findings | Improvements |
|-------|------:|--------:|--------:|------------:|
| CC2 | 23,955 | 145.7 | 12 | 8 |
| Codex | 7,904 | 380.4 | 8 | 7 |
| ChatGPT | 19,702 | 87.9 | 24 | 20 |
| Gemini | 6,332 | 38.5 | 4 | 3 |
| DeepSeek | 9,713 | 167.4 | 6 | 7 |
| **Total** | **67,606** | — | **54** | **45** |

**11 convergent themes (3+ models):**
1. Blind round contradicts providing findings (4/5) → Split R0A+R0B
2. Self-orchestration circularity (3/5) → Independent stop caps
3. Code extract scope insufficient (5/5, unanimous) → Full file delivery
4. Success criteria weak/circular (4/5) → Behaviour-based validation
5. Cross-model agreement not verification (3/5) → Downgrade to corroborative
6. SymPy partially applicable (3/5) → SymPy for math ops required
7. Fix ordering dependency-aware (3/5) → Build fix DAG
8. Missing telemetry (3/5) → Mandatory round-level logging
9. Need fault injection (4/5) → 4 canary scenarios
10. DeepSeek decomposition (5/5, unanimous) → 3-area decomposition
11. Load balancing separate with interface (5/5, unanimous) → Test separately

**Plan status:** APPROVED with all 11 themes integrated.

**Raw data:** `bench/logs/experiment_16/`
**Analysis:** `docs/experimental_notes/Exp16_Collation_Report_2026-03-30.md`

---

### Experiment 17: Immune Response Layer Validation + FFF Convergence

**Date:** 30–31 March 2026
**Models:** CC2 (Player Manager), Codex, ChatGPT, Gemini, DeepSeek (Players)
**Artifacts:** `dynamic_management.py` (full file), `verification_chain.py` (~910 lines)
**System prompt:** `cdsfl_core_formal.md` with FFF instructions
**Purpose:** Execute immune response layer validation under CDSFL with full code delivery, independent stop caps, and fault injection. Followed by FFF (Find-Fix-Follow) methodology test.

#### Design

Protocol: R0A (blind discovery) → R0B (seeded validation) → R1–N (adaptive rounds). Stop conditions: primary DynamicManager predicate + independent caps (10 rounds, 4h wall-clock). DeepSeek received 3-area decomposition (detection, response, integration). Pre-condition: 35 code fixes already applied from Exp 17 triage.

#### Results

| Metric | Standard confer | FFF rounds |
|--------|----------------|------------|
| Findings | 140 | 7 |
| Models | 5 | 2 (Gemini, CX) |
| Rounds | 4 (R3 complete, R4 partial) | 3 |
| Code fixes applied | 35 (4 batches) | 7 additional |
| Tests passing | 351 | 351 |

**Fix batches:**
1. 8 Immune Manager fixes (IM_F001–F013)
2. 9 Load Balancer fixes
3. 14 Verification Chain fixes
4. 4 Mathematical Model fixes

**FFF convergence (three-way round-robin: Gemini → CX GPT-5.4 → Gemini):** Converged in 3 rounds with 7 additional genuine fixes in already-reviewed code. Key FFF fixes: pathology_key routing (IM_F013), remediation escalation reset (IM_F002), verify_chain exception safety, estimate_gamma correction, kappa_rate divergence fix.

**Raw data:** `bench/logs/experiment_17/`, `bench/logs/experiment_18/`

---

### Experiment 18: Three-Way FFF Convergence Test

**Date:** 31 March 2026
**Models:** Gemini 3.1 Pro, CX GPT-5.4 (xhigh reasoning effort)
**Artifacts:** `dynamic_management.py` (6,354 lines), `verification_chain.py` (~910 lines)
**Purpose:** Formal test of FFF methodology. Hypothesis: FFF's resolution-and-consequence obligation forces cross-section tracing that standard multi-model confer does not achieve.

#### Design

Three-way round-robin under CDSFL with FFF instructions (find → fix → trace consequences). Pre-condition: 35 Exp 17 fixes already applied (codebase clean from standard confer).

#### Results

| Round | Model | Genuine Fixes | Key Findings |
|-------|-------|--------------|-------------|
| 1 | Gemini | 2 | `estimate_gamma` inf→1.0 clamping; `kappa_rate` divergence masking |
| 2 | CX GPT-5.4 (xhigh) | 5 | `verify_chain` exception safety; `Verifier.verify` type guard; `mu+novelty` routing key unreachable; `pm_performance_warning` unwired; `estimate_gamma` zero-data refinement |
| 3 | Gemini | 0 | Convergence declared (no findings >0.5 severity) |

**Summary:** 7 genuine fixes, 3 rounds, 2 models, 0 false positives, 351 tests passing.

**Model/effort configuration finding:** CX at o4-mini produced 0 genuine findings; GPT-5.4 with xhigh reasoning produced 5 genuine findings on the same code. FFF amplifies the capability gap between configurations.

**Cross-model refinement:** CX refined Gemini's `estimate_gamma` fix by identifying an edge case (zero-data vs perfect convergence distinction). This demonstrates FFF's multi-model value: the consequence-tracing obligation forces the second model to examine the first model's fix, not just the original code.

**Comparison with standard confer:** Standard Exp 17 confer (140 findings, 5 models, 4 rounds) → 35 fixes. FFF (7 findings, 2 models, 3 rounds) → 7 additional genuine fixes in code already reviewed by standard confer. FFF finds what confer misses.

**Raw data:** `bench/logs/experiment_18/`
**Analysis:** `docs/experimental_notes/Experiment_18_FFF_Convergence_Report_2026-03-31.md`

---

### Baseline Confer Runs 8–11 (Immune Pipeline Validation)

**Dates:** 2–4 April 2026
**Models:** CC2 (Opus 4.6), ChatGPT (GPT-5.4), Codex (GPT-5.4), Gemini (3.1 Pro), DeepSeek (V3.2)
**Artifact:** `bench/immune_agents.py` (immune pipeline, ~2,800 lines)
**System prompt:** `cdsfl_core_formal.md`
**Purpose:** Progressive validation of the immune pipeline under live conditions. Each run incorporated fixes from the previous run's diagnostics.

#### Summary

| Metric | Run 8 | Run 9 | Run 10 | Run 11 |
|--------|-------|-------|--------|--------|
| **Date** | 2 Apr | 3 Apr | 3 Apr | 4 Apr |
| **Rounds** | 20 | 20 | 7 | 2 |
| **Findings** | 339 | 425 | 237 | 59 |
| **Unique IDs** | 30 | 65 | 174 | — |
| **Churn** | 91.2% | 84.5% | 26.6% | — |
| **γ_novel** | −0.041 | +0.157 | +0.002 | +0.577 |
| **C(H,E)** | 0.789 | 0.828 | 0.889 | 0.873 |
| **Termination** | MAX_ROUNDS | MAX_ROUNDS | Convergence (R6) | Convergence (R1) |
| **Elapsed** | 52 min | 120 min | 37 min | 42 min |

#### Run 8 (2 April)

First baseline confer against the immune pipeline. 339 findings, 30 unique IDs — 91.2% churn. γ = −0.041 (no convergence). Task exhausted by Round 1 — models kept rewording the same findings. CC2 dominated (126 findings, amplification 1.613). Gemini benched R6, DeepSeek benched R10.

**Diagnostic:** Finding ID repetition was the primary churn mechanism. Convergence detection gap identified — no finding-ID-based convergence signal existed.

#### Run 9 (3 April)

425 findings, 65 unique IDs — 84.5% churn (improved from 91.2%). γ = +0.157 (sign flipped from Run 8). Terminated at MAX_ROUNDS. All 5 models contributed implementation-level findings (task packet fix worked). Gemini benched R5.

**Six infrastructure bugs identified:**
1. `continue` bypass — convergence check skipped for R5–R19
2. Hardcoded `tau_sim=0.8` — NK dedup unreachable
3. FSM terminal cascade from ABORT
4. B-Cell f-string escape — cell dead since creation (NameError in `_verify_z3`, hidden by silent `except: pass`)
5. Silent `except: pass` hid bug 4
6. No finding-ID convergence signal

All six fixed between Runs 9 and 10.

#### Run 10 (3 April) — Experiment 28

First natural convergence. 237 findings, 174 unique IDs — 26.6% churn. γ = +0.002. DM convergence at R6 (kappa=1.0). B-Cell revived with 86 verdicts (78 SymPy + 8 Z3).

**Per-model unique contributions:**

| Model | Findings | Unique | Unique Ratio |
|-------|----------|--------|-------------|
| Gemini | 20 | 18 | 90.0% |
| Codex | 52 | 45 | 86.5% |
| DeepSeek | 63 | 45 | 71.4% |
| CC2 | 36 | 26 | 72.2% |
| ChatGPT | 66 | 40 | 60.6% |

Every model contributed unique findings no other model found.

#### Run 11 (4 April) — Experiment 28b

Fastest convergence in bench history. 2 rounds, 59 findings, 42 minutes. γ_novel = 0.737 (highest), C(H,E) = 0.873. R0: 44 findings (5 models), R1: 15 findings (4 models — CC2 dispatch failure). 67% immune rejection in R1 (10/15 flagged DUPLICATE).

**CC2 dispatch failure:** Total timeout in R1 — 3× CLI timeouts at 300s, multi-turn fallback timed out at 600s, circuit breaker tripped. Root cause: ~358K char payload exceeding Python subprocess timeout. Led to CC2 timeout fix (300→900s, retries 3→1) as part of Exp 29 preparation.

**Shadow v2 data:** First production run of v2 immune components. NK v2 shadow caught 9 intra-round duplicates in R0 that v1 missed. B-Cell v2 ran 42 AST-grounded SMT-LIB checks. Data validated v2 activation for Exp 29.

**Raw data:** `bench/logs/baseline_confer_run{8,9,10,11}_*/`
**Analysis:** `experimental_notes/Run{8,9,10,11}_*.md`

---

### HIL Comparison Experiments: C1, C3, C4, C5 (4 April 2026)

**Date:** 4 April 2026
**Model:** Gemini 3.1 Pro (all conditions)
**Artifact:** `bench/immune_agents.py` (47,980 chars, 1,309 lines, pre-v2, commit 927bfbc)
**Purpose:** Compare interaction patterns under controlled conditions to test complementarity thesis.

#### Conditions

| Parameter | C1 (Realistic HIL) | C3 (CDSFL/FFF) | C4 (CDSFL + Meta Structured) |
|---|---|---|---|
| Protocol | 5 reactive developer prompts | 4 cells × 3 rounds | 4 cells × 4 rounds |
| Interaction | Developer dialogue (expert probing) | Automated (no interaction) | Structured certificate + FFF |
| Time | ~187s (~3 min) | ~540s (est.) | ~761s (~13 min) |
| Raw findings | 25 | 13 | ~27 (pre-falsification) |
| After FFF | 25 (no self-falsification) | 13 (5 SymPy proofs) | 16 (11 retracted) |
| Verified | 9/9 tested | 5/5 | 16/16 |
| False positives | 0 | 0 | 0 |

#### C5: Three-Layer Schema Validation

**Design:** Full conversational mode + CDSFL constraints + Meta structured prompting. Single continued session, no blind round, no cell decomposition. Predicted 30+ findings.

**Results:** 27 consolidated findings, 36/40 registry confirmed (90%), 6 novel, 0 false positives. 11.6 minutes. 5 cross-component findings. 100% include fixes.

**Novel findings:** Path traversal file read (C5-01), empty string bypass (C5-02), prompt injection via XML tags (C5-03), OOM via unbounded streaming (C5-23), nested JSON schema blindness (C5-05), Confident Hallucination Highway (3-bug cascade, C5-26).

**Novel constructs proposed:** Epistemic Routing Layer, Reconciliation Gate, Formalisation Agent, Typed LLM Classifier, Lazy Tool Discovery.

#### Complementarity Thesis

- C1 alone: ~25 verified findings (18 unique vs C4)
- C4 alone: 16 verified findings (14 unique vs C1)
- Union: ~33 unique verified findings — **32% more than best single condition**
- Overlap: only ~5 findings

C1 strength: cross-component interactions (5 unique pipeline-level bugs). C4 strength: formal per-component proofs (11 formal proofs). The two approaches find fundamentally different categories of bugs. **Complementarity thesis VALIDATED.**

#### Three-Layer Schema Discovery

Critical reframing of CDSFL methodology:
1. **Layer 1:** Meta structured prompting — reasoning format (premises, trace, conclude)
2. **Layer 2:** CDSFL constraints — rules of engagement (FFF, falsification, constraint classification)
3. **Layer 3:** Session architecture — full conversational mode as DEFAULT, ITC as FALLBACK ONLY

#### Interaction Patterns as Parameters

Subsequent analysis (4 April 2026) demonstrated that the 7+ interaction patterns tested across all experiments are not competing methodologies but user-configurable parameters within the CDSFL constraint box. The schema provides quality assurance regardless of pattern. The immune system, decay curves, and convergence detection are structurally pattern-agnostic. See `experimental_notes/Interaction_Patterns_As_Parameters_2026-04-04.md` for full analysis.

**Raw data:** `bench/logs/hil_comparison_c{1,4}_20260404/`, `bench/logs/c5_20260404T050417Z/`
**Analysis:** `experimental_notes/HIL_Comparison_Analysis_2026-04-04.md`, `experimental_notes/Master_Finding_Registry_2026-04-04.md`

---

*Raw data for all experiments is stored in `bench/results/` and `bench/logs/`. This document is the interpretive record. For the technical methodology, see the [white paper](../PAPER.md). For the experimental design rationale, see the [experiment plan memory file](../../.claude/projects/-Users-georgejackson-Developer-Projects/memory/cdsfl_experiment_plan.md). For the full experimental methods, see [PAPER.md Part X-A — Experimental Methods](../PAPER.md).*
