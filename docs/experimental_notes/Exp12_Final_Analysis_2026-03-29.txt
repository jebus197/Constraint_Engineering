# Experiment 12 Final Analysis — Complete 20 Round Run

**Date:** 29 March 2026
**Context:** Experiment 12, live run, 20 rounds complete with 5 models reviewing dynamic management layer at 3181 lines. 809 total findings. Terminated at MAX ROUNDS, not mathematical convergence.

---

## 1. Executive Summary

Experiment 12 ran to its arbitrary 20-round limit because all three convergence detectors were broken. Kappa stayed at zero permanently. Mu oscillated between 34 and 48 without trending downward. The novelty rate stop signal was not active in this run because it was committed as a fix during the experiment. Five models started. Only two survived to round 20. The dominant pattern was progressive model attrition due to context accumulation, not convergence.

Despite the broken termination, the experiment produced genuinely useful data. 809 findings across 21 rounds, with vocabulary novelty analysis confirming that CC2 was still producing genuinely new content at round 20, albeit at declining rates. The three committed fix categories — improved similarity, novelty rate stop signal, and immune response monitoring — are validated by this run and should prevent the same pathologies in subsequent experiments.

---

## 2. Model Performance

**CC2 (Opus 4.6)** — The workhorse. Present all 21 rounds. 337 findings total. Stabilised at approximately 15 findings per round from round 3 onward, dropping to 12–14 in the final rounds. Severity mean 0.707, no statistically significant trend. Abstraction mean 0.658, no significant trend. Vocabulary novelty declined from 23.9% at round 1 to 7.7% at round 20, confirming genuine diminishing returns but not yet exhaustion.

**ChatGPT (GPT-4o)** — Strong performer until context accumulation blocked it at round 17. 193 findings across 17 rounds. The only model showing statistically significant severity improvement: slope +0.004 per round, p = 0.0065. Severity rose from 0.664 in the blind round to a peak of 0.804 at round 14. Abstraction flat at mean 0.737. Blocked due to context exceeding feasibility threshold.

**Codex (GPT-5.4)** — Highest individual severity, mean 0.791. Blocked at round 13, P_feasible = 0.777. 72 findings across 13 rounds. Finding count declined from 16 in the blind round to 3 at round 12 — the sharpest convergence of any model. This is the behaviour you want (fewer but higher quality findings), but it was cut short by context blocking.

**DeepSeek** — Present all 21 rounds via area decomposition. 185 findings. Severity data sparse; many responses did not parse severity fields. Variable output quality, area-dependent. The decomposition strategy kept it alive throughout the experiment but its fingerprint collapsed entirely — all four dimensions near zero by round 20.

**Gemini 3.1 Pro** — Benched at round 5 by the failure handler. Tau was set to 150 seconds, threshold 225 seconds. Actual median latency approximately 250 seconds — it was always going to fail. Only 22 findings across 6 rounds. The highest average severity of any model at 0.857, but insufficient data to assess trends. The committed fix raises tau to 350 seconds, threshold 525 seconds.

---

## 3. Detector Failure Analysis

### 3.1 Kappa (Convergence Metric)

Kappa measures set-theoretic convergence using Jaccard similarity on finding descriptions. It was zero for every single round across 20 rounds. The problem is that Jaccard operates on exact word matches. Two descriptions of the same bug using different vocabulary score near zero similarity. Technical text with diverse phrasing will always defeat word-level Jaccard.

The committed fix adds stopword removal and bigram overlap, with combined scoring at 60% unigram + 40% bigram Jaccard. This will improve discrimination but does not solve the fundamental problem: lexical similarity cannot reliably detect semantic equivalence.

**Long-term fix:** embedding-based similarity. This requires a sentence embedding model (adding a dependency), but it is the only approach that can detect that "the EMA decays fingerprints" and "fingerprint values collapse due to exponential moving average" are the same finding.

### 3.2 Mu (Marginal Value)

Mu = change in yield / cost per round. It broke because of cost distortion from model attrition. When Gemini was benched at round 5, round cost dropped from approximately 5 model units to 4, but finding count stayed similar because remaining models compensated. Lower cost with similar yield means higher mu. The system interpreted losing a model as becoming more productive.

The same pattern repeated when Codex was blocked at round 13 (dropping to 3 active models) and when ChatGPT was blocked at round 17 (dropping to 2 models). Mu oscillated between 34 and 48 with no downward trend. The stop predicate for mu never came close to firing.

**CC2 confer assessment:** compute mu per model rather than per round. Aggregate via maximum across models. This eliminates the cost distortion because each model's marginal value is assessed independently. Approved as a HARD constraint fix.

### 3.3 Stop Predicate Overall

Neither kappa nor mu can terminate this class of experiment. The committed novelty rate fix provides a cost-decoupled signal, but its efficacy depends on the similarity function, which has the same Jaccard limitation as kappa. The vocabulary saturation metric proposed by CC2 — measuring cumulative unique vocabulary terms and triggering when the growth rate drops below threshold — is similarity-independent and should be implemented as an additional stop signal.

---

## 4. Fingerprint EMA Collapse

The capability fingerprint uses an exponential moving average with alpha = 0.3 to update four dimensions: D_decay, v_bar, A, and C. Over 20 rounds, this caused all models' fingerprints to collapse.

Mathematically, the initial value decays as `initial * 0.7^r`. After 20 rounds, `0.9 * 0.7^20 ≈ 0.0007`. When per-round observations are noisy or occasionally zero, the fingerprint decays toward zero regardless of actual model quality.

CC2 was the most dramatic example: v_bar collapsed from 0.9 to 0.0007. Only its consistency dimension C improved, from 0.8 to 0.998, because CC2 genuinely was consistent. DeepSeek's fingerprint collapsed entirely — all four dimensions near 0.001 by round 20 — which is numerically degenerate.

The collapse means the fingerprint cannot meaningfully distinguish models after approximately 10 rounds. Role assignment based on these values becomes arbitrary.

**Fix:** Replace EMA with a windowed mean over the last 5 rounds. This prevents ancient initial values from dominating while still tracking genuine changes. When all models fall below a minimum signal threshold, switch to round-robin assignment. CC2 classified this as HARD.

---

## 5. Self-Improvement Prediction Reassessment

**The prediction:** models will tend to self-improve under CDSFL, both in abstraction capacity and quality of findings.

With 9 rounds of data, two trends appeared significant: ChatGPT severity at p = 0.046 and CC2 abstraction at p = 0.045. With 20 rounds, CC2 abstraction lost significance entirely (p = 0.29). This is a textbook illustration of why small sample significance should be treated cautiously.

ChatGPT severity survived with p = 0.0065. However, this marginally fails Bonferroni correction for 8 simultaneous tests (threshold 0.00625), and has a critical confound: ChatGPT received increasingly rich prior findings context in later rounds. The improvement may be context-mediated rather than intrinsic model improvement.

**Verdict:** The prediction is not confirmed. One out of eight tests shows marginal significance with a known confound. The quality ratchet mechanism — where prior findings create a rising quality floor — is better described as environment-mediated improvement rather than model self-improvement. The CDSFL framework improves the input to each model rather than improving the model itself.

This is still useful. It means CDSFL produces improving output quality over rounds. But the mechanism is accumulated context, not model capability change. The model restart experiment (see item 10.5 below) would directly test this.

---

## 6. Churn Assessment

CC2 produced approximately 15 findings per round for 18 consecutive rounds. The question: is this churn, or genuine productivity?

**Vocabulary novelty analysis gives a clear answer.** CC2 early rounds (1–3) vs late rounds (18–20) show 33.5% Jaccard overlap. This means two-thirds of the vocabulary in late rounds was not present in early rounds. More precisely, 284 unique terms appeared in late rounds that were not used in early rounds.

Round-by-round novelty declined from 23.9% at round 1 to 7.7% at round 20 — a clear diminishing returns curve, but it never reached zero. CC2 was still introducing genuinely new terms and concepts at round 20.

Vocabulary overlap comparison across models:
- Codex: 15.9% (explored the most distinct territory)
- ChatGPT: 28.4%
- DeepSeek: 24.3%

**Verdict:** CC2 was not churning. It was producing genuinely different content with declining novelty. The consistent finding count of 15 per round reflects CC2's systematic exploration strategy rather than content recycling. The novelty rate decline confirms that stopping at rounds 12–15 would have captured most unique value with 3–5 fewer rounds.

---

## 7. Vocabulary Novelty as Stop Signal

The vocabulary novelty data provides exactly the stop signal the detectors could not.

**CC2 novelty trajectory (rounds 1–20):**
23.9, 19.4, 20.3, 17.1, 14.9, 17.6, 14.0, 16.4, 15.6, 12.5, 12.6, 9.8, 5.9, 9.0, 8.4, 10.4, 12.8, 10.7, 9.8, 7.7

Three distinct phases are visible:
- **Phase 1** (rounds 1–4): high novelty, above 17%
- **Phase 2** (rounds 5–11): moderate novelty, 12–18%
- **Phase 3** (rounds 12–20): low novelty, 6–13%

A stop threshold of 10% vocabulary novelty sustained for 3 consecutive rounds would have terminated at approximately round 14–15. This saves 5–6 rounds of diminishing returns while capturing approximately 90% of unique vocabulary.

This metric is similarity-function independent. It does not require comparing findings to prior findings using Jaccard or any other similarity measure. It simply counts new vocabulary terms per round against the cumulative term set. It is mechanically verifiable, cheap to compute, and robust to the semantic equivalence problem that defeated kappa and the finding-level novelty rate.

---

## 8. Model Attrition Pattern

The most operationally significant finding of Experiment 12 is the model attrition curve. Five models started. After 20 rounds, only two remained. The attrition was not planned.

- **Round 5:** Gemini benched — timeout threshold too aggressive
- **Round 13:** Codex blocked — context exceeded feasibility threshold
- **Round 17:** ChatGPT blocked — same context issue

This progressive loss of model diversity is the opposite of what the experiment design intended. The biodiversity hypothesis — validated in the three-architecture adversarial review — holds that different models find different classes of issues. Losing models means losing coverage.

The committed fixes address both causes: Gemini tau raised from 150 to 350 seconds; context windowing caps findings context at 150 items; adaptive decomposition extends area-focused dispatch to any model hitting context limits; model restart logic (the IT Crowd principle) adds the ability to start fresh instances with curated minimal context when quality degrades.

**For the next run, the prediction is that all 5 models should survive to the natural stop point with these fixes active.**

---

## 9. Lessons Formalised for Subsequent Runs

1. **Lexical similarity is insufficient for semantic duplicate detection.** Jaccard on word bags, even with stopwords removed and bigrams added, cannot reliably detect that two different phrasings describe the same finding. This is the root cause of kappa failure. Short-term mitigation: vocabulary saturation as a similarity-independent stop signal. Long-term fix: embedding-based similarity.

2. **Cost-coupled metrics break under model attrition.** Any metric defined as yield / cost will distort when the denominator changes for non-quality reasons. Compute per-model metrics and aggregate rather than computing system-level ratios.

3. **EMA with fixed alpha decays to zero over long experiments.** Replace with windowed statistics (mean over last W rounds) to maintain signal quality.

4. **Context accumulation is the primary model killer.** Over 20 rounds, prior findings context grows to exceed model context windows. Context windowing, decomposition, and model restart are all necessary defences.

5. **Model diversity is fragile.** Benching and blocking decisions must be conservative. False negatives (keeping a weak model active) cost much less than false positives (losing a productive model's coverage).

6. **Vocabulary novelty provides a robust, similarity-independent stop signal.** Implement as a primary stop criterion alongside the existing novelty rate.

7. **Twenty rounds is approximately correct for a 3181-line artifact** but should scale with artifact size. CC2 recommended `max_rounds = max(10, ceil(lines / 200))`. For 3181 lines this gives 16, which aligns with where vocabulary novelty dropped below 10%.

8. **The self-improvement prediction requires a controlled experiment to test.** The confound between context-mediated improvement and intrinsic model improvement can only be resolved by running models with and without prior findings context and comparing quality trajectories.

---

## 10. Next Steps

**10.1.** Implement vocabulary saturation as an additional stop signal. Highest priority — directly addresses the inability of all three existing detectors to terminate the experiment.

**10.2.** Replace fingerprint EMA with windowed mean. Second priority — fingerprint collapse makes model selection decisions unreliable after approximately 10 rounds.

**10.3.** Implement model restart logic. Third priority — context accumulation is the primary cause of model attrition.

**10.4.** Launch Experiment 12 second run with all committed fixes active, including the new vocabulary saturation signal, windowed fingerprint, and model restart. Predict natural termination at approximately round 14–16 for this artifact.

**10.5.** Design the controlled self-improvement test. Run the same artifact with and without prior findings context. Compare severity and abstraction trajectories to distinguish context-mediated improvement from intrinsic model improvement.

**10.6.** Evaluate embedding-based similarity for future runs. This is the long-term solution to the semantic equivalence problem but requires adding a dependency (a sentence embedding model) and validating it against the known duplicate pairs from this experiment.
