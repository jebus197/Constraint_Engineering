# Experiment 12 Live Wire Analysis — P-Pass Assessment with Extrapolation

**Date:** 29 March 2026

---

## Section 1. What Was Done

Experiment 12 is the first live orchestration test of the dynamic management layer built in Experiment 11. Five models ran under real distributed compute: CC2 as player manager, ChatGPT, Gemini, DeepSeek, and Codex as players. The artifact under review was `dynamic_management.py`, 3161 lines and 27 classes, which is the callable Python module CC2 implemented from the converged five-model design.

The experiment ran a single blind round followed by five adaptive rounds, producing 237 total findings across 29 system events. All five models remained active at termination. Termination was by max rounds, not by convergence detection.

---

## Section 2. Did the Experiment Produce Genuine Novelty?

Yes. The blind round produced 48 findings from all five models operating independently. These findings were architecturally diverse, covering different aspects of the module. CC2 produced the deepest output. Codex found the highest severity bugs, including finding F036 at severity 0.95 and finding F037 at severity 0.92, both targeting the failure handling path. This matches Codex's characterised cognitive mode of precision adversarial review.

The adaptive rounds then built on the blind round findings:
- **Round 1:** 37 findings, beginning to connect surface-level symptoms to underlying causes
- **Round 2:** 50 findings (peak), broadest coverage
- **Round 3:** 30 findings, higher abstraction, targeting structural issues rather than individual bugs
- **Rounds 4–5:** 36 findings each, increasing focus on invariant violations and cross-component interactions

This progression from surface to root cause to invariant is the ascending abstraction pattern the mathematical model predicts. It is not churn. The content of later rounds is qualitatively different from earlier rounds.

---

## Section 3. Was There Churn?

**Content-level churn: No.** The findings show clear progression. Early rounds found things like "missing error handling in specific methods." Later rounds found things like "the convergence detector using incompatible clustering modes across its own internal functions." These are not restatements. They are deeper analysis of the same system.

**Mathematical churn detection: Broken.** Three bugs in the detection machinery prevent the formal mechanisms from measuring what is actually happening.

**Bug 1:** The kappa convergence metric uses incompatible clustering. It compares flaw class sets from individual rounds against cumulative sets, which makes the overlap calculation meaningless. Kappa stayed below 0.5 across all rounds despite clear thematic convergence in the findings.

**Bug 2:** The duplicate detection function D_decay uses finding ID string matching to detect duplicates across rounds. Finding IDs are generated fresh each round, so they never match. D_decay registered high novelty even when findings were thematically related to previous rounds.

**Bug 3:** The structured output parser undercounts findings from ChatGPT and DeepSeek because their format variations do not match the expected pattern exactly. This suppresses the overlap signal that would feed into convergence detection.

The net effect: the experiment produced genuinely valuable findings but could not detect its own convergence. The mathematical machinery designed to prevent churn is itself broken, which means the experiment cannot self-terminate on convergence. It terminated on max rounds instead.

---

## Section 4. Fingerprint Evolution

The fingerprint updates tell an interesting story:

- **CC2:** Decay rate rose from 0.1 to 0.85, correctly identifying that CC2 was producing high overlap with prior findings by the later rounds. Verification score dropped from 0.9 to 0.15, reflecting that later-round findings are harder to verify automatically than early-round surface-level bugs.
- **ChatGPT:** Coverage score rose from 0.75 to 0.96 — the highest of any model — confirming its engineering pragmatism mode. It found the widest range of flaw classes.
- **DeepSeek:** Fingerprint degraded across all dimensions, from 0.8 accuracy to 0.16. This is partly real (DeepSeek was blocked from most rounds by the feasibility check because its 32K context window cannot fit the growing prompt) and partly an artefact of the blocked dispatch bug that created empty responses and triggered false failure detection. The fix applied mid-experiment stopped the bleeding but did not recover the already-degraded fingerprint.
- **Gemini:** Oscillated, producing 16 findings in one round and 1 in the next. Its final fingerprint shows low accuracy (0.44) and low coverage (0.44), but a timeout event in round 5 suggests infrastructure instability rather than genuine capability decline.
- **Codex:** Maintained the most stable fingerprint, with accuracy at 0.77 and coverage at 0.73, consistent with its characterised mode of precision review within a well-scoped window.

---

## Section 5. Extrapolation

### Part A. What Generalises

The ascending abstraction pattern — surface to root cause to invariant — appears to be a genuine property of multi-model distributed review under structured falsification. It was predicted by the mathematical model and observed in practice. If this holds across different artifacts and domains, it means that the value of later review rounds is not in finding more bugs but in finding deeper bugs. The count goes down. The severity and architectural significance go up. This is the opposite of churn.

The cognitive mode diversity hypothesis is further supported. Codex found the highest severity findings. ChatGPT found the widest coverage. CC2 found the deepest structural issues. Gemini found mathematical inconsistencies the others missed. DeepSeek, when it could participate, provided the iterative refinement perspective. No single model would have produced this spread. The coverage function D(n) approaches 1 through diversity of modes, not through scale of any single mode.

### Part B. Boundary Conditions

The convergence detection machinery must work correctly before the ascending abstraction claim can be made with confidence. Right now the pattern is inferred from content analysis rather than measured formally. The three detector bugs must be fixed and the experiment re-run with working instrumentation before the pattern can be claimed as measured rather than observed.

The DeepSeek allocation problem is not solved. Blocking DeepSeek entirely from adaptive rounds because the prompt exceeds 32K tokens wastes its demonstrated capability for iterative refinement. The task decomposition approach — giving DeepSeek focused subtasks within its window — has been discussed but not implemented.

### Part C. New Falsifiable Questions

1. Does fixing the three detector bugs and re-running the experiment produce formal convergence detection that matches the content-level convergence observed informally? If kappa reaches the convergence threshold with corrected clustering, that validates the mathematical model. If it does not, the model needs revision.

2. Does task decomposition for DeepSeek produce findings that the larger-context models miss? DeepSeek's iterative refinement mode on focused subtasks may find issues that holistic review overlooks. This is testable.

3. Does the ascending abstraction pattern hold on a different artifact? Running the same protocol on a different codebase would test whether this is a property of the method or an artefact of this specific artifact.

---

## Section 6. Recommendation

Fix the three detector bugs before continuing. The experiment produced genuine value, but continuing without working instrumentation means running blind. The detectors are the experiment's own feedback loop. Without them, there is no principled way to decide when to stop. The content analysis suggests we are approaching diminishing returns, with rounds 4 and 5 producing the same count at similar abstraction levels. But that assessment should be made by the mathematics, not by informal reading of the findings.

After the fixes, re-launch with the corrected detectors and let the convergence and diminishing-returns mechanisms make the termination decision. That is the whole point of the dynamic management layer. It should manage itself.
