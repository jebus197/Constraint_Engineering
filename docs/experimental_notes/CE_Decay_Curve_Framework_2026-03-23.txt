# The Inverse Square Root Law and AI Analytical Capability

**Date:** 23 March 2026

---

## Observation

During the Phase 2 smoke tests of the CDSFL methodology, an observation emerged from the data that connects to well established statistics.

The basic idea is simple. If you keep rolling a ball up an ever steeper hill, eventually the work you put in will clearly outweigh the reward for your effort. This is the law of diminishing returns. In statistics, it is formalised as the inverse square root law of precision: to halve the error, you must quadruple the measurements.

---

## Application to Iterative Review

This applies directly to iterative code and proof review. A reviewer doing genuine analysis will find fewer new issues in each successive round, because the easy-to-find problems are exhausted first. Round 1 catches the obvious errors. Round 2 catches subtler ones. By round 5, there is little left to find. The curve decays.

---

## Empirical Results

This is exactly what Codex 5.3 produced when reviewing a mathematical proof under the CDSFL framework. Its findings per round were **5, then 3, then 2, then 2, then 0** — a clear convergent curve. The model was exhausting a finite set of real issues.

DeepSeek V3.2 on the same task produced **2, then 2, then 2, then 2, then 2** — a perfectly flat line. The same number of new findings in every round for five rounds. This violates the inverse square root law. No genuine measurement process produces identical precision improvements forever.

The flat line is the mathematical signature of chatbot behaviour. The model is producing output because output is expected, not because there is something left to find. DeepSeek compounded this by simultaneously saying it agreed the review should stop while also presenting new findings — "I have nothing more to add" and "here are two more things" in the same response.

---

## The Activation Effect

The deeper finding was that CDSFL **activated** analytical capability in Codex that was dormant without the methodology. On the same task under control conditions with no CDSFL framework, Codex found almost nothing — zero findings in round 1, one in round 2, then nothing for three more rounds. Under CDSFL, the same model produced 5, 3, 2, 2, 0.

The methodology activated capability the model possessed but could not access without structure. DeepSeek showed no such activation. Its output was flat regardless of condition. The methodology can only activate capability that exists. It cannot create it.

---

## The Four-Part Capability Fingerprint

To measure this properly, we developed a four-part capability fingerprint.

**D — Decay Rate**
Measures how quickly the model exhausts the problem. Computed from the half-life of the decay curve: how many rounds until findings drop to half their initial rate. A flat line has D equal to zero. A steep decay has high D. A model that finds everything in round one has the highest possible D.

**v̄ — Mean Verification Score**
The fraction of the model's findings confirmed as correct by computational verification using SymPy. This separates real findings from confidently stated nonsense. A model can produce many findings, but if none of them are mathematically correct, it is not doing analysis.

**A — Total Novel Verified Findings**
How many real issues the model actually found across all rounds.

**C — Coverage**
The fraction of the total real issues in the artifact that were found. This is A divided by the estimated total real issues, computed from what all reviewers across all conditions found on the same task. This separates a model that found little because there was little to find from a model that found little because it missed most of what was there.

Together these four numbers provide a complete picture of analytical capability. No single number is sufficient. D tells you how quickly the model works. v̄ tells you whether what it finds is real. A tells you how much it found. C tells you what fraction of the total it caught.

---

## Connection to CDSFL's Own Mathematics

What struck me most about this framework is that the underlying mathematics was already present in CDSFL's own formulae. The G(n) formula models diminishing information gain per review round. It predicted decay for genuine analysis. The empirical data showed decay for genuine analysis. The theory and the observation agreed before anyone noticed they were describing the same thing. **The mathematics was hiding in plain sight.**

---

## Prediction

I predict that this pattern will hold across a much larger population of tasks and models. Our sample is small. But the signal is consistent and it connects to established statistical principles that hold universally. If diminishing returns apply to every genuine measurement process, and if chatbot churn violates diminishing returns, then the decay curve will distinguish genuine analytical capability from churn at any scale.

---

## Significance

If this prediction holds, what we are building is the beginnings of a science of AI computational analytics. CDSFL provides the controlled conditions under which analytical behaviour becomes observable. The decay curve provides the measurement. The verification chain provides the evidence. That is the structure of a science.

---

*TTS file saved for accessibility.*
