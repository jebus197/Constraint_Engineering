# CDSFL Mathematical Popper Analysis

**27 March 2026**

---

## The Core Question

Can Karl Popper's philosophy of falsification be mathematically modelled, and could such a model become the basis for domain expert configurations that machines respond to more efficiently than prose?

## The Short Answer

Yes. Parts of it are already modelled in our data. The decay curve we observe in CDSFL review rounds is the empirical trace of the falsification process. The question is not whether the mathematics exists, but which mathematical framework best captures it.

---

## What Was Found

Three mathematical frameworks were proposed by Gemini and tested by Codex 5.3 against actual bench data.

### Framework 1 — The Duane Non-Homogeneous Poisson Process

This models the discovery rate of errors as a power law that decays over rounds. The key parameter **gamma** tells you whether genuine convergence is happening:

- `gamma < 1` — the system is converging. Findings are getting harder to find because the easy ones have been eliminated.
- `gamma >= 1` — the system is not converging. The finding rate is constant or increasing, which means churn.

Codex tested this against bench data. On 18 CDSFL runs, the Duane model beat simple geometric decay in 17 out of 18 cases, with substantially lower prediction error. On CDSFL plus HIL runs, it beat geometric in 15 out of 18. For Control and HIL conditions, where rounds are self-iteration rather than confer, both models fit equally because the data mostly saturates in round 1.

This means the Duane model captures real structure in CDSFL review data that the simpler geometric model misses. The additional parameter (the re-injection rate, representing fixes that introduce new errors) is doing genuine work.

### Framework 2 — Mayo's Severity Function

This formalises what makes a test "good" in Popper's sense. A claim passes a severe test only if it would probably have failed the test if it were actually wrong. This is computable when SymPy verification is available. If SymPy checks a mathematical claim and finds it correct, the severity is high because SymPy would certainly have found it wrong if it were wrong.

Codex correctly noted that the simple statement "SymPy gives severity 1" is wrong. SymPy can verify a claim but cannot tell you what it would have found under different circumstances. True severity requires counterfactual reasoning. However, for deterministic verification (is this equation true or false?), severity approximates 1 and the distinction is academic.

### Framework 3 — KL Divergence for Human-in-the-Loop Interaction

This models the information gain from expert guidance as the divergence between the model's search distribution before and after receiving the hint. The framing bias we observed (where hints narrowed the search and reduced findings) is mathematically equivalent to **manifold collapse** — where the hint restricts the search space to a subregion and prevents the model from finding errors outside that region.

Codex noted that exact KL divergence is not computable from current data because we don't record probability distributions over hypotheses. A proxy is possible using flaw-class buckets, comparing the distribution of finding types with and without guidance. This is feasible but approximate.

---

## What This Means for Domain Expert Configs

If these mathematical frameworks can be calibrated from bench data, a domain expert configuration evolves from a verbal instruction set into a mathematical parameter set.

**Example — mathematics domain config:**
- Expected decay rate gamma: 0.2 to 0.5
- Expected difficulty distribution: bimodal (errors are either obvious or very subtle)
- Minimum rounds for corroboration: 3
- Severity threshold for stopping: 0.8

**Example — engineering domain config:**
- Expected decay rate gamma: 0.5 to 0.8
- Expected difficulty distribution: uniform (errors range smoothly from obvious to subtle)
- Expected re-injection rate beta: 0.1 (fixes sometimes introduce new issues)
- Minimum rounds for corroboration: 5

The machine does not need to understand falsification philosophically. It needs to match a mathematical signature empirically.

---

## Can Machines Respond Better to Formulas Than Prose?

Codex's answer: symbolic formulas in the Registry alone will not change model behaviour. The formulas must be wired into prompts, stopping logic, or feedback mechanisms.

This is correct but not the end of the story. The question is whether a prompt that says "produce findings at a rate that decays with gamma < 0.6" produces different behaviour from a prompt that says "try to disprove your conclusions and continue until diminishing returns." If the mathematical formulation gives weaker models a concrete, measurable target that the prose formulation does not, the mathematical encoding is more efficient. **This is testable.**

---

## What We Should Do

1. **Add the Duane model** as an analysis tool alongside the existing geometric model. Codex confirmed it fits data better and is computable from existing results.
2. **Keep the simple geometric model** as the primary diagnostic. It is interpretable and sufficient for most purposes.
3. **Use the Duane gamma parameter** as a domain characterisation metric. Different gamma values for different domains IS the mathematical encoding of how falsification works in each domain.
4. **Do not ship Mayo severity or KL divergence as canonical metrics yet.** Extend the data schema first to record the probability information these formulas require.
5. **Test symbolic versus prose directives** in the next smoke test. This is Gemini's key proposal and the direct test of whether mathematical Popper improves machine performance.

---

## Is This Pseudomaths?

No. Each component derives from established fields:
- Reliability engineering for the Duane model
- Frequentist statistics for Mayo's severity
- Information theory for KL divergence

Codex verified the Duane model against real data and found it fits 17 out of 18 CDSFL runs better than the simple model. That is empirical validation, not pseudomathematics.

What remains unproven is whether the assembly of these components into a unified "mathematical Popper" produces genuine predictive power beyond what the individual components provide separately. The honest framing: the mathematics is sound, the calibration is incomplete, and the proof requires more data.

---

## The Deeper Implication

If Popper's method can be mathematically encoded and that encoding produces measurably better analytical results when applied to machines, the implication extends beyond CDSFL. It suggests that epistemological frameworks in general — not just Popper's — can be mathematically operationalised as machine cognitive configurations.

- Bayesian updating would be a different mathematical encoding with different parameters.
- Kuhnian paradigm shifts would be discontinuities in the decay function.

The Registry becomes a platform for competing mathematical epistemologies, each testable against bench data.

This is what CDSFL's schema agnosticism was designed for. The methodology invites its own disproof by providing the infrastructure to test alternatives. If a competing mathematical epistemology produces steeper decay curves with higher verification scores, it wins. Popper is not sacred. Effectiveness is.
