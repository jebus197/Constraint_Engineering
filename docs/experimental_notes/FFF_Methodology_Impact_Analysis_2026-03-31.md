# Find-Fix-Follow: What It Did, What It Found, and Why It Matters

*31 March 2026*

## 1. What Find-Fix-Follow Actually Is

Before FFF, the standard CDSFL protocol worked like this: a model receives a body of work, produces a list of findings, and hands them back. Another model reviews those findings. A third model reviews the reviews. Repeat until nothing new surfaces. This is **confer**. It works — it got us through Experiments 12–16 and produced hundreds of genuine fixes.

But it has a structural limitation. Each model only *reports* what it sees. It does not fix anything during its turn. It does not explore what happens after the fix is applied. The resolution, and the consequences of that resolution, are handled later by someone else — usually CC as orchestrator.

FFF changes this. Each model is now required to do three things in a single turn:

1. **Find** the issue. Describe it precisely, with evidence.
2. **Fix** it. Produce the actual corrected text, code, or formula. Not a suggestion — the fix itself.
3. **Follow** the consequences. Once you have written the fix, ask yourself what it breaks, what it enables, and what new issues it creates. Report those too.

This was originally observed in the founder's informal sessions with Gemini. The pattern: find a problem in the mathematical appendix → Gemini fixes it → Gemini says "but now that we've changed this, the namespace collides with §7, and also the reduction property no longer holds cleanly." That *follow* step was where the real value appeared. The scope expanded within a single model turn instead of requiring another round-trip.

## 2. The Evidence: What FFF Actually Produced

Two distinct FFF applications provide comparison data.

### The Mathematical Audit (Rounds 7–8)

Before FFF, Rounds 0–6 used standard confer protocol. Five models, multiple rounds, SymPy verification. By Round 6: 8 items resolved, 2 minor editorial items remaining. Conventional protocol had converged.

**Round 7 applied FFF.** Same model (Gemini). Same appendix. Same resolutions. Only change: instruction format.

Gemini found **6 integration issues** that six previous rounds had missed:

| Issue | Description | Why FFF Found It |
|-------|-------------|-----------------|
| **Namespace collisions** | 8 variables reused across sections (β in 3 contexts, α/γ similar, k as index/rate/multiplier) | Follow step traced fix through every referencing section |
| **C(n) independence contradiction** | Base probability assumed independence; extended sections assumed correlation | Follow step forced tracing probability through both paths |
| **Synthesis deferral missing** | No penalty for context loss in decomposed dispatch | Follow step revealed optimisation threshold |
| **Null set evaluation** | Zero findings → undefined states in S_sync, O_A, yield weighting | Follow step traced through full formula chain |
| **Circular suppression guard** | S_sync referenced itself through fallback chain | Follow step untangled dependency |
| **Missing separability axiom** | Diversity discount treated as monolithic; correlations unbounded | Follow step required decomposition to apply fix |

SymPy 10/10 PASS after all fixes. Gemini declared model mathematically coherent and complete.

**Round 8** used FFF to evaluate 9 new constructs from earlier sessions:

| Verdict | Constructs | Rationale |
|---------|-----------|-----------|
| **3 ADOPT** | Seeded defect injection, NMI diversity, sycophancy trigger | Closed gap between theoretical parameters and empirical observables |
| **3 MODIFY** | Error re-injection, HIL framing penalty, substrate ceiling | Valid concept, needed integration with existing formalism |
| **3 REJECT** | Mayo severity, calibration ω, optimal stopping | Redundant with existing §4/§0.1/§7.8, §1 Bayesian propagation, §7.4 respectively |

SymPy 6/6 PASS. Total audit: 8 rounds, 39 algebra checks, all passing.

### Experiment 17 Code Fixes: Three-Way FFF Convergence

After applying 35 code fixes (8 IM + 9 LB + 14 VC + 4 MM), three-way FFF round-robin:

**Round 1 (Gemini FFF):** 2 findings
- `estimate_gamma` returned `inf` instead of `1.0` for perfect convergence
- `kappa_rate` returned `0.0` masking genuine divergence

**Round 2 (CX GPT-5.4 xhigh FFF):** 5 findings
- Refined Gemini's `estimate_gamma` fix (zero-data ≠ converged)
- `verify_chain` exception safety for malformed digests
- `Verifier.verify` type guard for non-string signatures
- `mu+novelty` routing key unreachable
- `pm_performance_warning` unwired

**Round 3 (Gemini):** Convergence declared. No new findings above 0.5 severity.

**Comparison:** Standard Exp 17 triage: 140 findings, 5 models, 4 rounds → 35 fixes. FFF convergence: 7 findings, 2 models, 3 rounds → 7 additional fixes, all genuine.

## 3. What Would Not Have Been Found Without FFF

**Strong cases:**
- **Namespace collisions** — 5 models × 6 rounds missed 8 variable reuses because each reviewed sections in isolation. FFF's follow step forced cross-section tracing.
- **C(n) independence contradiction** — Confirmed by SymPy as genuine mathematical contradiction. Five models, including two reviewing correlation sections, missed it.
- **CX refinement of Gemini's fix** — Gemini's `estimate_gamma` fix was valid in isolation. CX's follow step found the zero-data edge case within Gemini's fix.
- **Unreachable `mu+novelty` routing** — Exp 17 generated the finding but not the diagnosis routing. FFF's follow step forced tracing from detection to response.

**Softer cases:**
- Synthesis deferral, null set guards, separability axiom — might eventually have appeared in further conventional rounds, but had not after six.

## 4. Why FFF Works

Three mechanisms:

1. **Resolution obligation eliminates the handoff gap.** The model that finds the problem also fixes it and checks the fix. No information lost in translation.

2. **Consequence tracing forces cross-section analysis.** When required to trace fix consequences, models must read every referencing section — not just the section where the issue lives.

3. **Round compression.** Each FFF round does more work per turn. Round 7 alone produced more integration-level findings than Rounds 4–6 combined.

## 5. What FFF Does Not Do

- Does not replace multi-model review (CX's refinement of Gemini's fix proves this)
- Does not guarantee completeness
- Increases cognitive load per turn — weaker models may perform worse (CX o4-mini: all false positives; CX GPT-5.4 xhigh: 5 genuine findings)

## 6. Extrapolation

### What generalises
- FFF formalises how experienced engineers actually review: find → think about the fix → think about what the fix breaks
- Transfers to any structured review process: peer review, safety audits, regulatory compliance
- Round compression has direct economic implications (3 rounds vs 6 = half the compute)

### Boundary conditions
- FFF breaks when follow requires knowledge outside the model's context window
- Weaker models may produce wrong fixes and confidently follow wrong consequences — needs quality gate (SymPy/cross-model review under CDSFL)

### New falsifiable questions
1. Does FFF reduce rounds-to-convergence in controlled experiment?
2. Is there a model capability threshold below which FFF degrades?
3. Does FFF transfer to human review teams?

All registered as Experiment 19 (formal 2-condition FFF hypothesis test) / Bench Run 2 candidates. The FFF convergence work described in this document is now formally Experiment 18.

## 7. Project Implications

- Mathematical appendix: 826 → 1022 lines (normalised Ising, empirical anchoring, synthesis deferral, null guards)
- Codebase: 7 additional fixes beyond 35 from standard triage
- Methodology: FFF documented, tested, reproducible across mathematics and code with 3 models
- Next: wire into orchestrator as configurable mode → Experiment 19 formal evaluation (2-condition: standard vs FFF)
