# CDSFL Meta-Test Analysis

**27 March 2026**

---

## What Happened

The CDSFL mathematical model underwent its first full instrumented self-examination. Five AI models were given the complete 699-line mathematical appendix in a blind pass. Three produced valid structured output: Gemini 3.1 Pro, DeepSeek V3.2, and CC2 (another instance of Opus 4.6). Eleven genuine fixes were found, verified using SymPy, and applied.

The two most serious were an inverted sycophancy meter and an impossible condition on a cumulative count. The framework's novel constructs in sections 7 and 8 contained all the errors. The formalised-from-prior-art sections 1 through 6 had none that were found.

---

## Falsification of the Meta-Test's Own Claims

### Claim 1 — The framework examined itself

It didn't. The mathematical appendix was examined. The bench harness, the constraint registry, and the pipeline code were not part of the blind pass. What was tested is the theoretical foundation, the formulas. That is the right thing to test first, but calling it "the framework examining itself" overclaims.

**Corrected:** the framework's mathematical foundations were examined by multiple architectures.

### Claim 2 — Eleven genuine fixes, all verified

Each was either computationally verified using SymPy or logically demonstrated. Cumulative counts cannot decrease — that is provable by definition. The S-sync inversion was found independently by two models (Gemini and CC2), which is strong cross-architecture confirmation. Fix 5 (the second-order cognitive claim qualification) is editorial rather than mathematical. It changes an assertion to a conditional. But it is correct — you cannot claim empirical evidence that does not yet exist.

**Verdict:** survives. All 11 are genuine improvements. No false positives.

### Claim 3 — CC2 was the strongest performer

By count and yield, yes. CC2 had 16 findings, total yield of 280.6, and 8 unique findings. But CC2's verification rate was 0.75 compared to Gemini's 1.00. Gemini was more precise — every Gemini finding verified. CC2 produced more findings but at lower precision. "Strongest" depends on whether you weight volume or precision.

There is a deeper problem. CC2 is the same architecture as CC1, the scorer. CC1 designed the abstraction index H(x). CC1 scored CC2's findings using H(x). If H(x) systematically favours the type of findings that Opus 4.6 produces — deep structural analysis over surface verification — the ranking is architecturally self-reinforcing. SymPy breaks this for verified or falsified results, but the depth ranking is CC1's judgement.

**Verdict:** partially survives. CC2 genuinely found more issues. But "strongest" is metric-dependent and the scorer shares CC2's architecture.

### Claim 4 — Genuine biodiversity; each model found issues the others missed

The non-overlapping finding sets are real:
- Gemini found computation errors (table values, probability bounds)
- DeepSeek found logical insufficiencies (quantitative conditions, statistical thresholds)
- CC2 found structural gaps and edge cases (termination modes, mutual suppression, confounded metrics)

Only S-sync was independently found by two models.

But with only 3 models and 16 findings, non-overlap could be sampling variance rather than architectural diversity. You cannot distinguish genuine capability differentiation from each model randomly sampling from possible findings at this sample size.

**Verdict:** consistent with genuine differentiation, not conclusive at N=3.

### Claim 5 — Emergence was not confirmed. Correct null result

Composite yield was 249.0, which is lower than CC2's individual yield of 280.6. The composite is lower because averaging in Gemini's and DeepSeek's lower-depth findings dilutes the mean abstraction depth. The updated emergence condition correctly requires exceeding the union plus a statistical margin.

**Verdict:** survives. But reveals a tension in Y(t) as an emergence metric when model performance is highly skewed.

### Claim 6 — Core detection machinery in sections 1 through 6 proved robust

Absence of findings does not equal absence of errors. The game plan directed models toward sections 7 and 8 as highest-risk targets. Sections 1 through 6 may simply be undertested. "Proved robust" is overclaimed.

**Corrected:** no issues were found in sections 1 through 6.

### Claim 7 — CX contamination was detected by the framework

CX's findings were word-for-word identical to Gemini's. Any deduplication or any human glancing at the two outputs would catch this. The Adoption Delta of approximately 1.0 is the framework's formal metric for this, and it would detect partial contamination that visual inspection would miss. But in this case, the detection was trivial.

**Verdict:** the framework has the right metric. It was not needed here but would be in less obvious cases.

---

## Dispassionate Analysis

Strip away all framing. What actually happened is that three AI models independently reviewed a 699-line mathematical document. They found 16 issues, 11 of them genuine. Two other models failed to produce usable output. The issues were fixed and committed.

This is multi-model code review — sophisticated, instrumented, but fundamentally peer review of a technical document by three independent reviewers.

**The novel elements are three:**
1. The structured measurement of the review process itself
2. The demonstration that different architectures find different classes of errors
3. The framework detecting reviewer contamination with its own metrics

**The strongest evidence is not the 11 fixes.** Any competent mathematical reviewer, human or AI, would find an inverted formula or a probability exceeding 1. The strongest evidence is:

- **Complementarity is real.** Each architecture found things the others did not. This is useful operational knowledge for anyone running multi-model review.
- **H(x) ranked correctly.** Deep structural findings (Adoption Delta confound, termination modes) scored higher than notation cleanup (subscript errors, symbol renaming). The abstraction index measured what it claimed to measure.
- **Self-referential measurement partially works.** The framework measuring its own reviewers is inherently circular, but SymPy breaks the circle for verifiable claims. For non-verifiable claims, the circularity remains.

**The weakest points:**
- N=3 is too small for statistical claims about biodiversity or architecture-specific capability
- No external calibration — H(x) rankings have not been validated against human expert rankings
- Scorer-reviewer architecture overlap — CC1 scoring CC2's findings with a metric CC1 designed
- Operational framework untested — the bench harness, pipeline code, and constraint registry were not reviewed
- No confer round — the emergence hypothesis remains untested

The experiment was worth running. The fixes are real. But the meta-test's measurement of the meta-test is self-referential in ways SymPy does not fully resolve.

---

## Extrapolation

### What generalises

**The inverted meter pattern.** A measurement that silently produces the opposite of its intended signal is a general class of bug in any instrumentation system. The S-sync inversion would have corrupted every downstream sycophancy measurement while appearing to function correctly. Any novel measurement framework should be tested for sign inversions and monotonicity violations before deployment.

**Multi-architecture review finds different classes of errors.** If you review anything with one model, you inherit that model's blind spots. Three architectures found three distinct error classes. This has direct operational value for anyone building AI-assisted review pipelines: run at least two architecturally distinct models and take the union.

**Format compliance as a capability dimension.** Two of five models failed to produce usable output — one due to sandbox contamination, one due to format non-compliance. Structured output reliability varies dramatically across models. Any automated pipeline that depends on structured model output needs to treat format compliance as a first-class requirement, not an assumption.

### Boundary conditions

- The biodiversity hypothesis requires five or more valid models with repeated trials to reach statistical significance. At N=3, the signal is consistent but not conclusive.
- Self-examination has a hard boundary at design choices. SymPy breaks circularity for mathematical claims. For the five deferred items, no amount of model review resolves them — they require human design decisions.
- The meta-test tested formulas, not code. The gap between the mathematical model and its implementation remains untested.

### New falsifiable questions

1. Would a confer round produce genuinely new findings that no model found independently?
2. Would the same three models, given the corrected appendix, find new issues in a second blind pass?
3. Does H(x) ranking correlate with human expert ranking of finding importance?
4. Would architecturally novel models find yet more unique issues, or converge on the same set?
5. Do the 11 fixes change any operational measurements when the framework is applied to real benchmark data?
6. Does the Python bench harness correctly implement the corrected formulas? This may be the highest-value next test.

---

## Discussion Points

Five things to decide:

1. **Confer round.** Run it or stop? The blind pass found 11 genuine fixes, more than expected. The confer round would test the emergence hypothesis but costs API calls and time. Recommendation: worth running once with the three valid models, but not urgent. The mathematical fixes are done.

2. **Deferred items.** Five items cannot be resolved by more model review. They are design choices: the Adoption Delta confound, mutual suppression, dual termination, D symbol collision, and O_A discontinuity. All need human judgement.

3. **Implementation fidelity test.** The meta-test reviewed the spec but not the code. The bench harness implements these formulas. The 11 fixes to the appendix have not been propagated to the code. This is the most immediate practical gap.

4. **H(x) external calibration.** No human expert has ranked the 16 findings independently. Without this, H(x) is self-assessed. The founder could rank them and compute correlation.

5. **Priority stack.** The meta-test has completed priority 1 from the existing plan. The confer round is optional. The round-robin convergence test and Phase 2 experiment launch are the next items.
