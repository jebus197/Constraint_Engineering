# CE (Constraint Engineering / CDSFL) Foundational Principles

**Compiled:** 2026-03-19 05:26 UTC
**Source:** `EXPERIMENT_DESIGN.md`, `EXTENDED_RATIONALE.md`, `FOUNDERS_NOTES.md`, memory files

---

## Principle 1: CDSFL is Non-Canonical

CDSFL is not a finished product. It is a starting point — a hypothesis that says methodology itself can be formalised, and that this formalisation alone is a potentially worthwhile area of study.

The current schema, the formal document, the working directives, and the benchmark harness constitute the first iteration, not the final form. CDSFL is open to improvement from all sources:
- Self-generated improvement, where the methodology is applied to itself (empirically demonstrated through the CC, CX, and Gemini review cycle)
- Second and third party improvement from other researchers, teams, and organisations
- Both human and machine contributors, because any sufficiently competent agent can contribute to the methodology's evolution

Nothing about CDSFL is non-falsifiable. The methodology must evolve through the same falsification process it prescribes. If CDSFL cannot survive its own methodology, it fails its own test.

---

## Principle 2: Schema Competition

The founder's position, stated 19 March 2026: **there can be as many competing schemas as there are stars in the sky. Let them compete. May only the fittest survive.** The challenge is welcome, even if it means complete extinction of the current iteration of CDSFL itself.

This is not rhetorical modesty. It is the logical conclusion of a framework built on Popperian falsification. A methodology that claims immunity from the process it prescribes is self-refuting. A methodology that welcomes its own potential extinction under competitive pressure is consistent with its own deepest principle. The selection pressure that CDSFL applies to AI models — differentiating genuine constraint reasoning from confident fluency — applies equally to CDSFL itself. If a better methodology emerges, CDSFL's proper response is not resistance but recognition.

---

## Principle 3: Intelligence-Agnostic Human In the Loop

CDSFL's Human In the Loop role is functional, not species-restricted. A synthetic intelligence with sufficient domain competence IS a domain expert, not a simulation of one. This is an intrinsic design property, present since the framework's inception, not a future aspiration.

CDSFL is designed from the outset to allow for the emergence of machine intelligence as a fully trusted domain expert. The confer mechanism handles expertise boundaries: when any expert — human or AI — reaches the limit of its competence, items are flagged for peer review. Human peer review is explicitly invited at the confer stage, not bypassed.

When CC (Claude) provides domain expert context in CDSFL workflows, this is a standard step in the confer paradigm, not a limitation or workaround. The quality of the HIL (whether human vs. AI or different AI architectures) is a separate variable, testable in subsequent rounds.

---

## Principle 4: Methodology Formalisation as a Research Area

The deeper hypothesis: **methodology itself** — the structured application of scientific discipline to cognitive work — can be captured in a document that any sufficiently capable agent can apply. This is distinct from:
- **Prompt engineering**, which encodes expertise in the prompt
- **Training**, which encodes expertise in the model weights

CDSFL encodes expertise in the **protocol**.

If this hypothesis holds, the methodology is transferable, auditable, and improvable as a document, independent of who applies it. If it fails, the value lies entirely in tacit expertise. The philosopher Michael Polanyi called this the paradox of tacit knowledge: "we know more than we can tell." If formalisation adds nothing, that failure is itself informative.

The self-test and frontier experiments are designed to discriminate between these outcomes.

---

## Principle 5: The Formalisation Gap (Polanyi's Paradox)

The working `CLAUDE.md` directives, evolved through months of practice, may capture tacit knowledge that the formal `cdsfl_core_formal.md` does not. The CC and CX review success may have come partly from these working directives rather than the formal document alone.

This gap is itself a testable hypothesis: does the formal document produce comparable results to the working directives when both are given to the same model on the same task? The self-test was designed to begin answering this question.

---

## Principle 6: Multi-Vendor Model Collaboration as Novel Occurrence

During CE benchmark development, a potentially unprecedented event occurred. Multiple vendor models — Anthropic's Claude via CC and CX, Google's Gemini via CLI — actively communicated through the IM service and confer mechanism, collaboratively improving shared schemas and workflows.

This is not prompt-chaining or pipeline orchestration. Each model independently reviewed the others' output under a shared methodology, identified issues the others missed, and fixes were integrated iteratively.

- CC and CX ran an 8-round adversarial review and found approximately 24 issues, with convergence: 10, 7, 3, 3, 1, 2, 2, 1.
- Gemini ran a 5-round adversarial review and found **16 novel issues** that all 8 CC/CX rounds had missed, with convergence: 9, 10, 5, 4, 3.
- The Extended P-Pass across 5 modules found 4 additional actionable items.

This validates the **biodiversity hypothesis**: heterogeneous cognitive architectures find different defects than monoculture review. The significance extends beyond code review. The protocol — heterogeneous reviewers, shared methodology, defer-on-deadlock, and consensus stopping — is architecture-agnostic and domain-agnostic.

---

## Principle 7: Self-Improvement Under Distributed Compute

The CC, CX, and Gemini review cycle constitutes empirical evidence that software — and potentially any schema — can be automatically self-improving under CDSFL with distributed compute. The mechanism: diverse architectures apply the same falsification methodology to each other's output, converging on diminishing returns through adversarial collaboration.

Three falsifiable conditions for this claim were identified and P-passed:

1. **Convergence:** The review cycle must show measurable diminishing returns. It does, as the convergence curves show.
2. **Coverage:** Heterogeneous architectures must find issues homogeneous review misses. They do, as Gemini's 16 novel issues demonstrate.
3. **Generalisability:** The mechanism must work on problems other than code review. This is the next thing to test, via the frontier task set.

The round-robin convergence test is designed to formalise and extend this observation.

---

## Where These Principles Are Documented

- **`EXPERIMENT_DESIGN.md`** (`bench/` directory): Foundational principles section plus the self-test design and results.
- **`EXTENDED_RATIONALE.md`** (`docs/`): General-audience companion essay, updated with multi-vendor collaboration, intelligence-agnostic HIL, methodology formalisation, non-canonical nature, and schema competition.
- **`FOUNDERS_NOTES.md`** (`docs/`): The founder's own framing, updated with non-canonical nature, intelligence-agnostic HIL, multi-vendor collaboration, methodology formalisation, and schema competition.
- **Memory files** (`~/.claude/projects/.../memory/`): `cdsfl_intelligence_agnostic.md` and `cdsfl_selftest_results.md`, both updated with schema competition principle and all foundational context.
- **This accessibility file:** All eight principles, boundary conditions, and five falsifiable questions consolidated in plain text for TTS recovery.

---

## Principle 8: Complexity Threshold Hypothesis

The self-test suggests a complexity threshold below which methodology formalisation adds no measurable value. On an 805-line code review task — below CDSFL's design point — all conditions capped at approximately 40% recall regardless of methodology.

The threshold may correlate with `constraint count × constraint interaction density`. Problems where constraints are few or independent do not benefit from structured falsification. Problems where constraints are numerous and interact non-linearly — the problems CDSFL was designed for — benefit substantially.

This is a testable prediction. The 25 frontier tasks (10–50% expected single-pass accuracy across five categories) are designed to locate this threshold empirically. If CDSFL's contribution correlates with task category (Proof > Synthesis > Design > Code > Reasoning-about-reasoning), then the threshold's shape becomes visible.

---

## Boundary Conditions

- **Schema competition** requires a selection mechanism — the benchmark. Without objective measurement, competition degenerates into preference. The benchmark harness IS the fitness function.

- **The intelligence-agnostic HIL principle** depends on models actually having sufficient domain competence. At current capability levels, this holds for some domains (code, mathematics, well-documented engineering) and may not hold for novel research, tacit craft knowledge, or safety-critical domains where no historical precedent exists. The boundary moves as models improve.

- **The self-improvement under distributed compute claim** is bounded by the diminishing returns curve. It works until architectures exhaust their complementary blind spots. After convergence, adding more architectures adds cost without coverage.

---

## Five New Falsifiable Questions (19 March 2026)

1. **Does schema competition produce better schemas?** Testable by giving two competing methodology documents to the same model on the same task and measuring which produces better outcomes. The benchmark harness already supports this.

2. **Does the intelligence-agnostic expert role hold at frontier difficulty?** On genuinely hard problems (the 25 frontier tasks), does AI-provided domain expertise match human-provided domain expertise? Testable in the next experimental round.

3. **Where does the complexity threshold sit?** Is there a problem complexity below which methodology formalisation adds nothing measurable? The frontier tasks span five difficulty categories. If methodology contribution correlates with task category, this reveals the threshold's shape.

4. **Does multi-architecture review generalise beyond code?** The biodiversity hypothesis was validated on software review. Does it hold for mathematical proof, engineering design, chemical synthesis, and self-referential verification? Testable via Schema C on the frontier task set.

5. **Is there a convergence limit for heterogeneous review?** The self-improvement mechanism works until architectures exhaust their complementary blind spots. Where is this limit? Measurable from the round-robin convergence test.

---

## Where All of This is Now Documented

- **`PAPER.md`:** Part 11 (Frontier Research Directions) covers methodology formalisation, intelligence-agnostic expert role, multi-architecture cognitive convergence and biodiversity hypothesis, schema competition, complexity threshold hypothesis, and all five open falsifiable questions. The Invitation to Falsify section includes these as explicit falsifiable assertions.
- **`README.md`:** New Frontier Research Directions section covers schema competition, biodiversity hypothesis, intelligence-agnostic expert role, and open questions with reference to PAPER.md Part 11.
- **`EXPERIMENT_DESIGN.md`:** Complexity Threshold Hypothesis section, boundary conditions, and all five open falsifiable questions added before the self-test section.
- **`EXTENDED_RATIONALE.md`:** Five new paragraphs covering multi-vendor collaboration, self-improvement under distributed compute, intelligence-agnostic HIL, methodology formalisation, non-canonical nature, and schema competition.
- **`FOUNDERS_NOTES.md`:** New sections on non-canonical nature with schema competition, intelligence-agnostic HIL, multi-vendor collaboration, methodology formalisation, complexity threshold, and all five falsifiable questions.
- **Memory files:** `cdsfl_intelligence_agnostic.md` and `cdsfl_selftest_results.md` updated with schema competition principle and all foundational context.
