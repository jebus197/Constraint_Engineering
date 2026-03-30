# CDSFL Phase 2 Smoke Test Results Discussion

**Date:** 23 March 2026

---

## What Was Tested

The smoke test ran 3 tasks across 4 conditions, giving 12 runs total. Each run involved three reviewer models working independently: Opus 4.6 (Claude Code), Codex 5.3, and DeepSeek V3.2. The three tasks were a mathematical proof (Erdos-Szekeres theorem), a coding problem (interval scheduling with weighted dependencies), and a cross-domain engineering task (solar-powered water purification system).

The four conditions were:

- **Control:** Raw prompt, no structure, no guidance
- **HIL:** Brief expert guidance capped at 500 characters, simulating a knowledgeable human
- **CDSFL:** Formal falsification framework with computational verification but no domain expertise
- **CDSFL + HIL:** The full methodology with structure, guidance, external research, and verification

---

## The Headline Numbers

**Total findings across all 12 runs:** 283 unique HARD findings.

| Condition | Total Findings |
|---|---|
| Control | 104 |
| HIL | 38 |
| CDSFL | 73 |
| CDSFL + HIL | 68 |

At first glance, Control appears to have found the most issues. This is the wrong interpretation.

---

## Why Control Found More

Control ran all 5 rounds on every task because nothing converged. The models kept producing output because the protocol kept asking them to, and without any convergence mechanism there was no reason to stop. CDSFL + HIL stopped at an average of 4.33 rounds because the models actually converged. When findings genuinely decayed to zero, the protocol stopped.

More output from non-convergent review equals more volume, not more quality. Without computational verification scores (which were missing from this test — see below), we cannot definitively prove that Control's 104 findings are lower quality than CDSFL + HIL's 68. But the decay curve shapes are diagnostic.

---

## The Decay Curve Analysis

We examined the round-by-round finding counts for each model under each condition and classified each curve as:

- **Monotone decay:** findings decrease or stay constant each round, eventually reaching zero
- **Flat:** same number every round, indicating churn
- **Non-monotone:** erratic spikes and drops, indicating neither genuine convergence nor consistent churn

**Corrected decay rates across all three models:**

| Condition | Decay Curves | Total Curves | Rate |
|---|---|---|---|
| Control | 3 | 9 | 33% |
| HIL | 5 | 9 | 56% |
| CDSFL | 5 | 9 | 56% |
| CDSFL + HIL | 8 | 9 | 89% |

This is a monotonic gradient from Control to the full methodology. The more structure and guidance a condition provides, the more likely the models are to produce convergent analytical behaviour rather than erratic or flat output.

---

## What the Models Did

**DeepSeek V3.2** was the clearest case. Under Control on the maths task, it produced 2, 2, 2, 2, 2 — a perfectly flat line. The same number of new findings every round regardless of whether there was anything left to find. This is the mathematical signature of chatbot behaviour: producing output because output is expected, not because there is something to report.

Under CDSFL + HIL on the same task, DeepSeek produced 3, 2, 0 — a clean decay curve. The methodology converted chatbot churn into genuine convergence. **This was the single most striking finding in the data.** A model that defaults to flat output under control conditions produced convergent analytical behaviour when given the full CDSFL framework.

**Codex 5.3** was more mixed. Under Control it produced non-monotone curves on 2 of 3 tasks, with erratic spikes. Under CDSFL + HIL it produced decay on 2 of 3 tasks and flat-at-zero on 1 (meaning it found nothing, which is not churn but genuine inability on that specific task). Overall, Codex performed best under CDSFL + HIL.

**Opus 4.6** (Claude Code) showed the most surprising result. Under Control, it produced non-monotone curves on all 3 tasks, including dramatic spikes at late rounds (for example, 11, 7, 0, 0, 6 on the engineering task, with a spike of 6 at round 5). Even a frontier reasoning model produces erratic output without structure. Under CDSFL + HIL, Opus produced decay on 2 of 3 tasks, with only the engineering task remaining non-monotone.

---

## Statistical Significance

Codex 5.3 ran a McNemar exact test on the paired data (same task-model cells across conditions). Control vs CDSFL + HIL gives p = 0.0625 two-sided, which is not significant at the conventional p < 0.05 threshold. One-sided gives p = 0.03125, which is significant only if the directional hypothesis was pre-registered. A Cochran Q test across all four conditions gives p ≈ 0.0449, which is borderline.

**The honest assessment:** this is suggestive evidence, not definitive confirmation. The sample size (9 paired observations per condition) is too small for robust statistical inference. The full bench test of 26 tasks will provide 78 paired observations, which should resolve the significance question.

---

## The Verification Gap

The most serious methodological issue with this smoke test is that the SymPy verification kernel, while implemented and correctly wired, produced no usable output. The verification function ran on every CDSFL and CDSFL + HIL finding but returned a determinate count of zero every time. This happened because the CDSFL review prompts never asked the models to produce verifiable claim fields in their findings. The models produced findings with claim text, evidence, severity, and proposed checks, but never included a structured mathematical claim that SymPy could parse and verify.

This means the `v-bar` component (mean verification score) of the `(D, v-bar, A, C)` capability fingerprint is entirely missing from this dataset. We have D (the decay rate), A (total findings), and we can compute C (coverage). But without `v-bar`, we cannot distinguish verified findings from confidently stated nonsense. The decay curves tell us whether models are converging, but not whether what they converge on is correct.

**This must be fixed before the full bench run.** The CDSFL blind and confer prompts need to include a `verifiable_claim` field with a structured format that SymPy can parse. Findings without either a verifiable claim or an explicit unverifiable reason should be flagged as incomplete.

---

## SymPy vs Wolfram

We tested both SymPy (open source, MIT licensed) and Wolfram Alpha on the same exponential decay fit. The parameters agreed to 6 decimal places: `a = 7.948143`, `lambda = 0.471934`. The R-squared values differed slightly (SymPy gave 0.989, Wolfram gave 0.997) due to different fitting algorithms, but both indicated excellent fit. SymPy is a valid stand-in for Wolfram for this class of computation.

---

## The Proposed SymPy Feedback Loop

A significant enhancement for the full bench run: instead of SymPy passively scoring findings after extraction, feed the verification results back to each reviewer model between rounds. Currently the flow is:

> model reviews → produces findings → SymPy scores → score used for stop rule

The proposed flow is:

> model reviews → produces findings → SymPy verifies each finding → results fed back to model → model revises analysis in light of computational evidence → produces refined findings for next round

This mirrors what a real domain expert does. A physicist reviewing a proof does not just eyeball it — they compute the bounds, check the algebra, verify against known results, and revise their assessment based on what the computation shows. The SymPy feedback loop formalises this workflow. It is available to CDSFL and CDSFL + HIL conditions only. Control and HIL do not get computational feedback.

Combined with the step-by-step tutor methodology (presenting findings one at a time rather than dumping everything at once), this creates a closed loop of review → verify → revise → repeat, with each step small enough for the model to process without context window exhaustion.

---

## What This Means for the Full Bench Run

Six specific fixes are needed before launching the full 26-task bench test:

1. Add `verifiable_claim` to the CDSFL blind and confer prompts with a structured format that SymPy can parse.
2. Require either a verifiable claim or an explicit unverifiable reason for every HARD finding under CDSFL conditions.
3. Add a coverage gate: flag CDSFL runs where zero findings have determinate verification across all rounds.
4. Implement the SymPy feedback loop for CDSFL and CDSFL + HIL conditions.
5. Fix the counting bug in the analysis script that double-counted curves due to loose condition name matching.
6. Ensure flat curves (same number every round) are classified as churn, not decay, in the analysis.

The full bench run at 26 tasks across 4 conditions gives 104 runs. At the smoke test rate of approximately 30 minutes per run, this is roughly 50–55 hours, or about 2–2.5 days. The decay curve analysis, once the verification gap is closed, will have 78 paired observations per condition comparison, which should resolve the statistical significance question that the smoke test left open.

---

## Broader Implications

The smoke test accomplished what smoke tests are for: it identified methodological gaps before committing to the full experiment. The signal is promising. CDSFL + HIL produces convergent analytical behaviour 89% of the time versus 33% for unstructured review. The methodology activates convergent behaviour even in a chatbot (DeepSeek) that defaults to churn. But without computational verification of finding quality, we cannot distinguish genuine analysis from convincing-looking convergence. The verification layer is not optional. It is the difference between measuring something real and measuring appearances.

The full bench run, with all six fixes applied, will produce the data needed to answer the central question: does CDSFL + HIL produce measurably better and externally verifiable results than unstructured review? The smoke test says probably. The bench test will say definitively.
