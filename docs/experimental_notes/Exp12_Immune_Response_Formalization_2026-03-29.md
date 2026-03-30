# CDSFL Detector Health Monitor — Mathematical Immune Response Formalization

**Date:** 29 March 2026
**Context:** Experiment 12, second live run with fixes. Dynamic management layer, 3181 lines, 27 classes, 5 models.

---

## 1. The Problem We Observed

Experiment 12 ran its first iteration with three broken detectors.

**Kappa** (the convergence metric) was stuck at zero for every round. The Jaccard word-level similarity function could not detect semantic duplicates in technical text. Two descriptions of the same bug using different vocabulary scored near zero similarity. The convergence detector never saw duplicates and reported zero convergence indefinitely.

**Mu** (the marginal value metric) was increasing instead of decreasing. When Gemini was benched for timeout, the round cost dropped but finding counts stayed the same. Since mu = change in yield / cost, lower cost meant higher mu. The system thought it was becoming more productive after losing a model.

**The failure handler** benched Gemini after two timeout events. Gemini's tau was set to 150 seconds, giving a threshold of 225 seconds. Its actual median latency was 250 seconds. It was always going to exceed the threshold. But Gemini was still producing genuine findings. Slow is not useless.

The experiment would never terminate mathematically. It would churn to the maximum of 20 rounds.

---

## 2. The Three-Level Architecture

**Level 0.** The models review the artifact. This is the experiment itself. Five models examine 3181 lines of code and produce findings.

**Level 1.** The convergence and diminishing returns detectors monitor Level 0. Kappa measures whether models are still finding new things. Mu measures whether the marginal value per round justifies the cost. D_decay measures how many findings are duplicates.

**Level 2.** The Detector Health Monitor watches Level 1. This is the immune response. When kappa is stuck, when mu increases paradoxically, when detectors disagree, Level 2 detects the pathology and emits a diagnosis.

Level 2 does not require its own convergence detection because it uses simple statistical signatures: trajectory analysis. Is the value stuck? Is it going the wrong direction? Do two independent signals disagree? These are mechanically verifiable checks that do not require their own monitoring layer. The recursion terminates here.

---

## 3. Mathematical Formalization

Let D = {kappa, mu, novelty_rate, D_decay} be the set of detectors.

For each detector d in D, let h(d, r) be its output value at round r.

**Three pathology signatures:**

**Stuck pathology:**
```
stuck(d, W) = True when ∀ r' ∈ [r-W, r]: |h(d, r') - h(d, r'-1)| < ε
```
The detector output is not changing despite active input.

**Diverging pathology:**
```
diverging(d, W) = True when ∀ r' ∈ [r-W, r]: h(d, r') > h(d, r'-1)
```
For detectors expected to decrease toward zero, this means the metric is going the wrong direction.

**Disagreement pathology:**
```
disagreement(d1, d2) = True when sign(Δh(d1)) ≠ sign(Δh(d2))
```
Two independent measures of the same underlying quantity should trend in the same direction.

---

## 4. Adaptive Sensitivity

The immune response itself must be adaptive. A static monitor with fixed thresholds is just another detector that can break.

**Biological analogy:**
- Innate immunity provides fixed, fast, broad responses.
- Adaptive immunity learns from exposure.
- Regulatory T cells prevent the immune system from attacking healthy tissue.

The Detector Health Monitor implements all three.

**Innate response.** The fixed checks: kappa = 0 for W rounds; mu increasing for W rounds. These fire immediately on pattern match.

**Adaptive response.** The effective detection window adjusts based on experience:

```
W_effective(d) = max(2, floor(W_base + resolved_count(d) * sensitivity_growth_factor))
```

When a pathology appears and then resolves naturally, the resolved count increases and the window widens. The monitor becomes less trigger-happy for that detector — it learned that the pathology was transient.

When a pathology persists across multiple detection cycles, the persistence count increases and the severity escalates. First occurrence is a warning. Second and subsequent occurrences are critical. The monitor learned that this is a real problem.

**Regulatory mechanism.** When a diagnosis is emitted and the pathology subsequently resolves, the monitor records the resolution. Future diagnoses for the same detector type require more evidence (longer window) before firing. This prevents the monitor from generating noise.

---

## 5. What Changed in the Code

**Fix 1.** Gemini tau raised from 150 to 350 seconds. Threshold becomes 525 seconds. Gemini will no longer be benched for its normal operating latency.

**Fix 2.** Similarity function improved. Stopword removal eliminates high-frequency words that inflate Jaccard without carrying semantic content. Bigram overlap captures phrase-level similarity. Combined score: 60% unigram Jaccard + 40% bigram Jaccard. Same-class bonus reduced from 0.4 to 0.3 to account for the improved discrimination.

**Fix 3.** Novelty rate added as a cost-decoupled convergence signal. For each new finding, compute maximum similarity to all prior findings. If maximum similarity is below `tau_novelty = 0.65`, the finding is novel. The novelty rate is the fraction of novel findings per round. When it drops below `tau_novelty_stop = 0.15`, the stop predicate fires regardless of mu. This is immune to cost distortions from model benching.

**Fix 4.** `DetectorHealthMonitor` class added. Watches kappa, mu, and novelty rate trajectories. Detects stuck, diverging, and disagreement pathologies. Adaptive sensitivity via resolved and persistent pathology tracking. Emits structured diagnoses through the event stream.

**Fix 5.** Stop predicate updated:
- Original: Stop when smoothed mu < tau_mu
- New: Stop when smoothed mu < tau_mu **OR** smoothed novelty rate < tau_novelty_stop

Either signal is sufficient. This prevents the experiment from running to max rounds when one detector is broken.

---

## 6. Strategy for Subsequent Runs

The immune response learns across rounds within a single experiment run. It does not yet learn across experiment runs. For subsequent runs, carry forward:

- The resolved and persistent counts from prior runs, as initial state for the health monitor. This gives the monitor memory across experiments.
- The similarity function thresholds (tau_sim and tau_novelty), calibrated from observed similarity distributions. After each experiment, compute the distribution of finding similarities and adjust thresholds to the natural gap between duplicate and novel clusters.
- The timeout thresholds per model, calibrated from observed latency distributions. Use the 95th percentile of actual response times as the basis for tau, not a static estimate.
- The novelty rate trajectory as a baseline. If a new experiment on the same artifact shows higher novelty rate than a prior experiment, the artifact may have changed or the models are exploring differently. If lower, convergence is faster.

---

## 7. The Deeper Insight

The founder identified that CDSFL should be self-healing. This is the same as saying the scientific method should be able to correct its own instruments. A thermometer that reads zero regardless of temperature is useless. A scientist who does not notice the thermometer is broken is worse than useless. The Detector Health Monitor is the scientist watching the thermometers.

The adaptive sensitivity is the scientist getting better at distinguishing real temperature changes from instrument drift. The resolution tracking is the scientist learning which thermometer readings are transient noise and which indicate genuine dysfunction.

This is not recursive ad infinitum. Level 2 uses mechanically verifiable trajectory checks. It does not need a Level 3 watching it because its own checks are simple enough to be provably correct. The recursion grounds out in statistics. This is analogous to how the scientific method itself is not falsifiable by the scientific method — it is validated by its track record of producing reliable knowledge. The immune response is validated by its track record of correctly diagnosing detector dysfunction.
