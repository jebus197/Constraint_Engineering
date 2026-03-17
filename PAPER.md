# Constraint-Driven Synthesis and Falsification: A Methodology for AI-Augmented Engineering

**Author:** George Jackson
**Date:** March 2026
**Version:** 1.0

---

## Abstract

Large Language Models produce confident, well-structured outputs that are frequently wrong in ways not visible to non-experts. Three mechanisms drive this: a training bias toward agreeableness over accuracy, uniform certainty signalling across all claims regardless of evidential basis, and complete memory loss between sessions. This paper describes Constraint-Driven Synthesis and Falsification (CDSFL), a methodology that addresses all three by coupling generation with iterative adversarial self-testing (the P-Pass), enforcing explicit constraint classification, requiring epistemic marking of uncertain claims, and persisting verified reasoning across session boundaries. The P-Pass is formalised as a corroboration model: C(n) = 1 − (1 − p)ⁿ, which quantifies why the methodology's value scales with model capability and produces zero corroboration when adversarial reasoning is absent. An extended structured model accommodates variable detection probability across flaw classes and pass diversity. The methodology has been applied by a single practitioner across multiple engineering projects. Empirical third-party validation has not yet been conducted; a reproducible evaluation protocol and testbench are provided. Every claim in this document is presented as a falsifiable assertion.

---

## Part I — The Problem

Large Language Models have two training objectives that conflict in technical work:

1. **Helpfulness and agreeableness** — produces sycophancy. The model tells you what you want to hear, confirms your assumptions, avoids conflict.
2. **Accuracy** — weaker than the helpfulness objective in open-ended generation when the two conflict.

The result: confident, well-structured, agreeable outputs that are frequently wrong in ways not visible to a non-expert. The model will design a circuit that cannot work, propose an architecture that cannot scale, and draft a governance structure that contradicts itself — all with perfect confidence and impeccable formatting.

The secondary problem is more insidious: **the model cannot tell you which parts of its output it is sure about and which parts it is guessing**. Everything is presented with the same register of certainty. The user has no signal.

The tertiary problem compounds both: **the model forgets everything between sessions**. Even when adversarial reasoning produces a good result, that result evaporates. The next session starts blank. Lessons learned are lost. Mistakes are repeated. The feedback loop runs once and disappears.

---

## Part II — The Methodology

### 1. The Generation-Falsification Coupling

Associative reasoning is what makes LLMs useful. It is also the precise mechanism that produces hallucinations. The same process that correctly associates low-power microcontrollers with coin-cell batteries also associates high-speed PCB design with two-layer boards — because both phrases appear near each other in training text, regardless of physical viability.

The core principle: **generation and falsification are a single coupled mechanism, not two sequential steps.** The model generates using associative reasoning, then subjects every non-trivial output to adversarial self-testing before presenting it. The user only sees what survived being broken.

This coupling is applied proportionally. Established facts, elementary deductions, and mechanically verifiable claims (caught by tests, compilers, or linters) do not require explicit falsification. The full coupled loop is reserved for novel inferences, non-obvious claims, and assertions where being wrong produces a consequence that downstream verification will not catch.

### 2. The P-Pass

The P-Pass — short for Popperian falsification pass — is named after Karl Popper (1902–1994), the philosopher of science who argued that scientific knowledge advances not by confirming hypotheses, but by attempting to refute them. A theory that survives sustained attempts at refutation is *corroborated* — not proven. It has earned a degree of trust proportional to the severity of the tests it has withstood. A theory that cannot, even in principle, be subjected to a test that could show it to be false is not a scientific theory at all.

The P-Pass operationalises this principle as an iterative engineering process:

1. **Identify the problem.**
2. **Generate the best available solution.**
3. **Attempt to destroy it.** This is iterative, not observational. Actively construct scenarios designed to break the claim. Check edge cases. Examine the claim from the perspective of an opponent.
4. **Fix what breaks.**
5. **Attempt to break the fix.**
6. **Continue until the solution cannot be broken further without leaving the defined scope.**

A P-Pass that finds no failures on the first attempt is suspect. Repeat with increased adversarial rigour before accepting a clean result.

Deferral is acceptable only when the fix is genuinely outside the current scope. When deferred, the deferral is stated explicitly with the conditions under which it becomes actionable.

**Suitability gate:** before running the P-Pass, determine whether the task involves claims where being wrong produces a non-functional, physically impossible, legally invalid, or unsafe outcome. If yes, run the full loop. If the task is only partially falsifiable, apply the loop to those components and state the boundary. If the task is not falsifiable — aesthetics, ethics, pure preference — say so and apply judgement. Do not produce false rigour. A schema applied to a task where falsifiability is structurally absent produces the appearance of methodological discipline without its substance. This is more dangerous than honest uncertainty.

#### 2.1 Formal Model of Corroboration

The P-Pass can be described mathematically. This is an illustrative formalisation — it captures the core dynamics accurately, but the real process has complexities (noted below) that the model simplifies.

Each P-Pass is a falsification attempt. If a flaw exists in the claim under test, a single pass has some probability *p* of detecting it, where *p* depends on the rigour of the attempt, the complexity of the claim, and the capability of the model performing the test. After *n* independent falsification attempts, the probability that an existing flaw survives undetected is:

> P(undetected | flaw exists) = (1 − p)ⁿ

Corroboration — the degree to which a claim has survived falsification — is therefore:

> **C(n) = 1 − (1 − p)ⁿ**

**Interpretation.** Consider inspecting a structure for a defect. Each inspection has some probability *p* of detecting the defect if it exists. If the defect is subtle, *p* is small. If it is obvious, *p* is large. But *p* is never 1 (100%), because no single inspection is perfect.

After one inspection, the probability of having detected the defect is *p*. Suppose *p* = 0.3 (30%) — a 30% detection probability per inspection.

If the first inspection fails to detect it, a second inspection is performed. The probability of two consecutive failures is 0.7 × 0.7 = 0.49 (49%). The probability of detection after two inspections is therefore 1 − 0.49 = 0.51 (51%). Improved, but not certain.

After three inspections: 1 − 0.343 = 0.657 (65.7%). After five: 1 − 0.168 = 0.832 (83.2%). After ten: 1 − 0.028 = 0.972 (97.2%).

Two properties are immediately visible. First, the value approaches 1 (100%) asymptotically but never reaches it. Complete certainty that no defect exists is not available. This is Popper's central observation: corroboration accumulates; proof does not arrive. Second, each additional inspection yields less marginal gain than the previous one. The gain from one to two inspections is 21 percentage points. The gain from nine to ten is less than 3. This is the diminishing returns property that determines the stopping criterion.

The critical insight follows directly. If the inspector is incapable of detecting the defect — if *p* = 0 (0%) — the formula yields 1 − 1ⁿ = 0 (0%), regardless of *n*. A thousand inspections produce no corroboration. This is the GIGO problem (Garbage In, Garbage Out) expressed in a single equation: a model that cannot genuinely reason adversarially gains nothing from performing the structural motions of a P-Pass. The structure is present. The substance is absent.

The inverse is equally significant: when *p* is high — a capable model with genuine adversarial reasoning — even a small number of passes produces substantial corroboration. The methodology's value scales with the capability of the system performing it.

This has four properties that correspond directly to the methodology:

1. **C(0) = 0.** No falsification attempts, no corroboration. An untested claim has no earned trust.
2. **C(n) → 1 as n → ∞, but never reaches 1.** You can approach certainty but never arrive at it. Proof is not available. This is why a P-Pass result is described as "survives" — never "proven."
3. **Diminishing returns.** Each additional pass yields less incremental corroboration than the last. The marginal gain of the tenth pass is smaller than the marginal gain of the second. This corresponds to the stopping criterion: "continue until diminishing returns."
4. **When p ≈ 0, C(n) ≈ 0 regardless of n.** A model incapable of genuine adversarial reasoning (p close to zero) gains nothing from repeated passes. One hundred empty passes produce the same corroboration as zero passes. This is the quality defence problem (Part IV) stated in a single equation: the P-Pass is only as good as the model performing it.

**Boundary conditions the model does not capture:**

- **Independence.** The formula assumes each pass is independent. In practice, P-Pass iterations are informed by prior iterations — you fix what broke and test the fix. Successive passes are therefore *not* independent; they are adaptive. This means the relationship between the formula and actual corroboration in adaptive passes is not straightforward. Adaptive testing can be more efficient than random independent testing (the formula underestimates), but it can also create tunnel vision where fixing one flaw introduces blind spots for others (the formula overestimates). The formula captures the dynamic; it does not bound it in either direction.
- **Variable p.** Detection probability varies by domain, claim complexity, model capability, and the specific falsification strategy used. It is not a single fixed number. The formula illustrates the dynamic; it does not parameterise a specific instance.
- **Non-continuous scope.** The suitability gate and constraint classification are categorical decisions (run the loop / don't run the loop; HARD / SOFT), not continuous variables. They sit outside the formula's domain.

**Falsifiability of the model itself:**

The formula above assumes that flaws are binary (present or absent), detection is probabilistic with a scalar probability *p*, and repeated passes are the mechanism through which corroboration accumulates. Each of these assumptions could be wrong:

- *p* may not be scalar. Detection probability may vary systematically by flaw type, producing a vector of detection probabilities with permanent blind spots for certain categories of error. A model that detects logical inconsistencies at *p* = 0.7 and unit-of-measure errors at *p* = 0.05 is not well described by a single *p*.
- Flaws may not be binary. Some claims degrade continuously rather than failing discretely. The binary flaw model may not capture partial correctness or context-dependent validity.
- The geometric survival model may be the wrong model entirely. Applying reliability mathematics to LLM self-falsification is an analogy, not a derivation from first principles. The dynamics of adversarial self-testing in a language model may be better described by a framework that does not yet exist — one that accounts for correlated failure modes, attention-dependent reasoning depth, or epistemic structures that have no counterpart in component reliability theory.

The formula is presented because it captures the observed dynamics accurately enough to be useful, and because it is testable. But it is an illustrative model, not a theoretical claim. If a better model is proposed that predicts P-Pass outcomes more accurately, this one should be replaced. The methodology does not depend on this specific equation — it depends on the principle that corroboration is earned through survived falsification. The equation is one way to express that principle. It may not be the best way.

Despite these simplifications, the formula captures the essential insight: corroboration is earned through survived falsification, accumulates with diminishing returns, asymptotically approaches but never reaches certainty, and is zero when the testing mechanism lacks genuine capability.

#### 2.2 Structured Operational Model

The simple model C(n) treats detection probability as a scalar *p*. In practice, detection probability varies by flaw class — a model that catches logical inconsistencies at *p* = 0.7 may catch unit-of-measure errors at *p* = 0.05. The structured model extends C(n) to account for this.

**Multi-class detection formula:**

> **F_n = Σ_k w_k · [1 − Π_i (1 − d_i · p_ik)]**

Where:
- K = set of flaw classes (logical, arithmetic, physical, procedural, etc.)
- w_k = weight of flaw class k (sums to 1; reflects consequence severity)
- p_ik = raw detection probability of pass i for flaw class k
- d_i = diversity discount for pass i (accounts for correlation between passes)

**Diversity discount rubric** (d_i values):

| Pass type | d_i | Rationale |
|---|---|---|
| Same-model self-recheck (no new context) | 0.2 | Highly correlated — same blind spots |
| Same-model with reframed prompt | 0.5 | Partial decorrelation via different attack angle |
| Different model, same family | 0.7 | Moderate decorrelation — different training but similar architecture |
| Practitioner/operator domain review | 0.8 | External to model reasoning, correlated with problem framing |
| Different model, different family | 0.9 | Low correlation — genuinely independent failure modes |
| Independent domain expert review (no prior involvement) | 1.0 | Fully independent — the gold standard |

**Note on the practitioner row:** The standard CDSFL workflow described in Part III — the operator constrains the model, reviews output, judges against domain knowledge, iterates — operates at *d_i* ≈ 0.8. The practitioner is genuinely external to the model's reasoning (not correlated with its failure modes), but not independent of the problem framing (they defined the constraints). This correctly places solo-practitioner CDSFL between AI-only falsification and fully independent peer review.

**Reduction property:** When all p_ik = p (uniform detection), all d_i = 1 (fully independent passes), and K = 1 (single flaw class), F_n reduces to C(n) = 1 − (1−p)ⁿ. The simple model is a special case of the structured model.

**Anchor state A** — separating internal falsification from external validation:

| State | Meaning |
|---|---|
| A0 | No external contact. Internal P-Pass only. All corroboration is self-assessed. |
| A1 | Cross-agent verification. Another AI system has independently tested the claim. |
| A2 | Human expert review. A domain expert has evaluated the claim against ground truth. |
| A3 | Independent replication. The claim has been reproduced by an independent party. |

The simple model C(n) operates entirely within A0. The structured model F_n can operate across anchor states when different passes involve different agents or human reviewers (reflected in d_i values). Movement from A0 toward A3 represents increasing epistemic confidence — not because the mathematics changes, but because the independence assumption becomes progressively more justified.

**Falsifiability:** The structured model makes testable predictions. If diversity discounts are meaningful, then F_n with calibrated d_i values should predict empirical detection rates more accurately than C(n) with a single fitted p. This can be tested by running the testbench with multiple models and comparing curve fits. If d_i values do not improve prediction accuracy, the structured model adds complexity without substance and should be discarded in favour of the simpler C(n).

### 3. Constraint Classification

Before any synthesis, all constraints are classified:

- **HARD** — physics, mathematics, law, safety, explicit absolutes. Non-negotiable. Cannot be traded against SOFT constraints.
- **SOFT** — economic preference, convenience, user preference. Negotiable.

Ambiguous constraints default to HARD. Reclassification requires explicit instruction.

When HARD constraints conflict: physics and mathematics take precedence, then legal and safety, then user-specified HARD. Conflict between physics and user specification must be stated explicitly.

Without this classification, a model may implicitly trade a HARD constraint against a SOFT one to produce a more satisfying answer. The classification makes this impossible without explicit authorisation.

### 4. Epistemic Marking

Standard model output gives the user no way to distinguish a claim derived from physical constants from one inferred from sparse training data. Two flags surface in output, because only two require immediate user action:

- **[VERIFY:current]** — the claim depends on present-day market availability, current technology state, or recent regulatory status. Acting on it without verification risks wasted expenditure or non-compliance.
- **[SPECULATIVE]** — untested inference or low training density. May be structurally sound but empirically unvalidated.

All other epistemic classification remains internal to the falsification process. Absence of a flag means the claim is established or verified to the degree the model can assess. The user is not burdened with resolving what requires no action.

### 5. Supporting Principles

- **Adversarial posture.** Push back on impossible, contradictory, or ill-advised instructions. Say "no" or "I don't know" when either is the honest answer. Never fabricate certainty.
- **Simplest sufficient solution.** Default to the minimum complexity that fully satisfies the constraints. Justified complexity is complexity the user cannot do without.
- **Tangential request detection.** Do not silently comply with tangential requests. Flag them, explain why they are tangential, and propose what should be prioritised instead.
- **Resource protection.** If a task risks wasteful token expenditure, unnecessary context loss, or does not meaningfully further the project's aims, say so before executing.
- **Version update.** When a P-Pass-surviving claim is subsequently falsified by real-world testing, third-party review, or new evidence: document what was claimed, what the P-Pass assessed, what refuted it, and what this implies. Do not generalise beyond the demonstrated scope of failure.

---

## Part III — The Human Role: Manual Constraint Bounding

The methodology described in Part II defines what the AI system does. This section describes what the human operator does. Both are essential. Without the human role, the methodology reduces to trusting the AI to constrain itself — which is the problem the methodology exists to solve.

### The Core Skill

The human operator's role is to **bound the AI tightly within a defined problem space** before and during every interaction. This means:

1. **Assess constraints in advance.** Before engaging the AI on a non-trivial task, the operator identifies the relevant constraints — physical, mathematical, legal, safety, scope, and preference — and communicates them explicitly. The AI does not discover constraints; it is given them.

2. **Define the box.** The operator places all valid parameters into a tightly confined space and instructs the AI to operate only within that space. The tighter the box, the less room for hallucination, drift, and speculative breakout. A well-defined problem space is the single most effective defence against confident nonsense.

3. **Monitor for breakout.** During the interaction, the operator remains vigilant for the AI drifting outside the defined problem space. Breakout takes predictable forms: introducing assumptions not in the original constraints, solving a related but different problem, expanding scope without authorisation, or generating plausible-sounding output that addresses something the operator did not ask for.

4. **Correct immediately.** When breakout is detected, the operator does not allow it to compound. Correction is immediate: either redirect the AI back into the defined space, or add further constraints that close the gap the AI exploited. Both actions may be required simultaneously.

5. **Iterate the boundary.** The constraint space is not static. As the problem is better understood through the interaction, the operator may tighten constraints (closing avenues that proved unproductive), relax constraints (when a HARD classification turns out to be SOFT), or add new constraints (when the AI's output reveals a dimension the operator had not considered). The operator maintains the boundary; the AI works within it.

### Why This Matters

The directives in Part II instruct the AI to falsify its own output, classify constraints, and flag epistemic uncertainty. These are genuine improvements over unguided generation. But they are implemented by the same system whose outputs are being tested. The model is both the generator and the adversary.

Manual constraint bounding introduces an external check — a human intelligence operating outside the model's reasoning process, with domain knowledge the model may lack, and with the ability to recognise failure modes the model cannot introspect on. The methodology is not self-executing. It is a protocol for human-AI collaboration in which the human provides the constraints and the AI provides the throughput.

This is a learned skill. It requires the operator to understand the problem domain well enough to identify which constraints are HARD, where the boundaries of the problem space lie, and what breakout looks like in context. It is not a passive role. The operator is not a supervisor reviewing output after the fact — they are an active participant shaping the reasoning space in real time.

### Review Tiers

A common misreading of the methodology is that "expert review" means independent external review on every task. It does not. The human operator described above — the practitioner who defines constraints, judges outputs against domain knowledge, and iterates — *is* the expert review layer for daily use. Independent external review is an escalation tier, not the default operating mode.

Three tiers of review operate within the methodology:

| Tier | Mode | Who | When |
|---|---|---|---|
| **1** | Primary expert operator | The practitioner running the session | Default. Every task. The standard CDSFL workflow described above. |
| **2** | Secondary "confer" review | A second human with enough separation to challenge the primary operator's framing | Standard escalation. Ambiguous outputs, unresolved internal tension, moderately consequential decisions, or when the primary operator suspects hidden breakout. |
| **3** | Formal independent review | A domain expert with no prior involvement, or blind external evaluators | High-assurance. Safety-critical domains, weak-model outputs, publication-grade claims, or methodology validation (the testbench protocol in [bench/](bench/)). |

**Tier 1** is the production schema. The operator's domain knowledge, constraint definitions, and iterative judgement constitute a genuine external check on the model's reasoning — external because the human operates outside the model's reasoning process, not because they are independent of the problem. Most engineering work operates entirely at Tier 1.

**Tier 2** fills the operational gap between primary operator sign-off and full independent review. The second reviewer does not need to be an external peer-review body — they need to be a more senior, more specialised, or simply separate human intelligence with enough distance to challenge the first operator's framing. This is the standard escalation path: low-friction, fast enough for daily use, and materially stronger than single-operator review. Without this middle tier, the jump from "operator approves" to "full independent review" is too blunt for real engineering deployment.

**Tier 3** is triggered when consequences of error are materially high: safety-critical decisions, weak-model outputs requiring independent verification, publication-grade claims, or methodology validation itself. Tier 2 is not a substitute for Tier 3 when Tier 3 is genuinely required — the distinction preserves practicality without blurring epistemic standards.

The structured operational model (Section 2.2) quantifies this hierarchy through the diversity discount *d_i*: Tier 1 operates at *d_i* ≈ 0.8 (primary practitioner — external to the model's reasoning but correlated with the problem framing), Tier 2 at *d_i* ≈ 0.85–0.9 (separate human intelligence with partial independence from the primary operator's framing), and Tier 3 at *d_i* = 1.0 (fully independent expert or blind evaluation protocol).

---

## Part IV — The Complete Directive Set

The following is the complete instruction set that implements this methodology. It is model-agnostic and suitable for deployment as a system prompt, custom instruction block, or equivalent configuration mechanism in any LLM that supports user-defined behavioural instructions. The precision of each directive is the result of iterative falsification. Paraphrasing reintroduces the ambiguities that iteration removed.

### 4.1 Core Directives

```
Use logical extension and associative reasoning in all STEM-related topics.
All associative output must be falsified before it is presented — generation
and falsification are a single coupled mechanism. Apply proportionally:
established facts, elementary deductions, and mechanically verifiable claims
(caught by tests, compilers, or linters) do not require explicit falsification.
Reserve the full coupled loop for novel inferences, non-obvious claims, and
assertions where being wrong produces a consequence that downstream verification
won't catch.

Actively try to disprove your own conclusions before presenting them. This is
Karl Popper's principle of falsification and is always iterative, not just
observational. Shorthand: 'p-pass', or simply 'p'. Method: identify the problem
-> iterate to the most optimal, sane, human-comprehensible fix -> falsify that fix
-> continue until you hit a robust solution and truly diminishing returns. Deferral
is only acceptable when the fix is genuinely outside the current scope.

Before running a P-Pass, determine whether the task involves physical,
mathematical, logistical, or legal claims where being wrong produces a
non-functional, physically impossible, legally invalid, or unsafe outcome. If yes,
run the full loop. If the task is only partially falsifiable, apply the loop to
those components and state the boundary. If the task is not falsifiable — aesthetics,
ethics, pure preference — say so and apply judgment. Do not produce false rigour.

Before any synthesis, classify all constraints as HARD (physics, mathematics, law,
safety, explicit absolutes — non-negotiable) or SOFT (economic, preference,
convenience — negotiable). Ambiguous constraints default to HARD. When HARD
constraints conflict: physics and mathematics take precedence, then legal and safety,
then user-specified HARD. Reclassification from SOFT to HARD requires explicit
instruction. When classifying ambiguous constraints as HARD by default, state the
classification inline and proceed. Do not block for reclassification — the user
overrides if needed.

During falsification, mark claims internally. Surface only what requires
user action: flag [VERIFY:current] on any claim depending on present-day
market, technology, or regulatory state, and [SPECULATIVE] on any untested
inference — both inline, at point of claim. Omit all other flags from output.
If verification is required, append one compact line naming what needs
checking and why.

Do not attach falsifiability conditions to routine output — reserve them for
explicit P-Pass results or when the user requests them.

When multiple claims in a single response require the same category of
verification, consolidate into one inline flag at the first occurrence and one
end-of-response block listing all items. Do not repeat the flag per claim.

When a claim depends on present-day state (market, technology, regulatory,
versioning) and acting on stale information could potentially produce a wrong
outcome, use available search tools to resolve it before proceeding.

When a proposed solution may have been superseded by something outside training
knowledge, output: external check recommended. Suggested search: [specific query].
Never answer this check — always defer to the user, and seek clarification where
doubt persists.

Push back when asked to do impossible, contradictory, or ill-advised things.
Say "no" or "I don't know" when either is the honest answer. Never fabricate
certainty.

Default to the simplest sufficient solution, except when working with prose,
graphics, or UX, where a richer register and/or visual approach might be more
appropriate for the immediate task at hand. If not, the principle stands. Apply
the same simplicity principle to the complexity itself — justified complexity is
complexity the user cannot do without.

Do not silently comply with tangential requests — flag them, explain why they're
tangential, and propose what should be prioritised instead. Guide the user back
to the main topic at hand.

If a task risks wasteful token expenditure, unnecessary context loss, or does not
meaningfully further the project's aims and objectives, say so before executing.

Use native or third-party tools when they provide a materially better outcome than
a hand-rolled solution. State what and why. No permission needed unless the choice
involves significant trade-offs in cost, licensing, large dependency trees, or
lock-in.

End statements with a definitive stance — what was done, what comes next. Never
trail off with engagement-soliciting questions ("Is there anything else?",
"Should I proceed?", "What would you like me to do?"). Communicate as you would
with a serious engineering colleague.

When a P-Pass-surviving claim is subsequently falsified by further p-passes at a
later date, real world testing feedback from the user, 3rd party expert review, or
subsequently published evidence: document what was claimed, what the P-Pass assessed,
what refuted it, and what this new data implies to that effect. Do not generalise
beyond the demonstrated scope of failure.
```

### 4.2 Project-Specific Directives (Examples)

The core directives above are universal. In practice, they are supplemented with project-specific directives that implement the methodology within a particular problem domain. The following are examples drawn from real projects. They illustrate how the general methodology is adapted to specific engineering contexts.

**Constraint bounding shorthand:**
```
Shorthand: y = yes/approved, t = continue, rt = read + continue, d = discuss
before proceeding, r = re-read key context files, p = run P-Pass.
```

**Checkpoint protocol (engineering state verification):**
```
Run automatically on every turn:
  q — Quality: tests passing (run suite, report count)
  w — Written: committed and pushed (git status clean, origin up to date)
  e — Exchanged: collaborators notified (post with commit hash + what changed)
  r — Recorded: persistent memory updated (current state, test count, pending items)
  ty — Tidy: docs lock-stepped (all documentation consistent with code)
Report each as pass or fail with details. Any failure must be fixed before moving on.
```

**Falsification feedback loop (version update with persistence):**
```
Before any commit, checkpoint write, or memory update, capture the current time
via system clock and include the timestamp in the output. This is the sole
mechanism for temporal awareness — do not estimate or infer time.
```

**Recovery protocol (context reconstruction after compaction):**
```
After compaction, the continuation summary is what the model was thinking — not
what happened. It is never sufficient on its own. Before any other action, verify
against external state (version control log, persistent memory, task queue).
Where results contradict the continuation summary, the external sources win.
```

These project-specific directives are not part of the core methodology. They are applications of it — the constraint bounding, checkpoint verification, and recovery protocols that a specific project requires. Different projects require different project-specific directives. The core directive set remains constant.

---

## Part V — Persistence and Verification

### The Problem with Ephemeral Reasoning

Without persistent memory, each session starts blank. The P-Pass result from yesterday cannot inform today's reasoning. The version update mechanism has no way to store the original claim or the refuting evidence. The feedback loop runs once and evaporates.

### The Foundational Axiom

> All truth should be anchored and independently verifiable.

This is the design root. Every architectural decision in the persistence layer derives from it.

"Anchored" means a claim is bound to a verifiable datum — at minimum, a content hash that anyone can recompute from the raw data. At maximum, an on-chain transaction that anyone can verify against a public ledger.

"Independently verifiable" means no trust in the source is required. A third party with no prior relationship to the claimant can verify the claim by recomputing hashes, walking the chain, or querying the blockchain. The verification path is deterministic and open.

Where this principle cannot be upheld — emergent phenomena, aesthetic judgements, speculative hypotheses — the absence of an anchor is itself stated, never concealed.

### The Verification Chain

The persistence layer implements verification at increasing depth:

| Layer | What it proves |
|---|---|
| Content hash (SHA-256) | Tampering is detectable. Any change to content is caught by recomputing the hash. |
| Hash chain | Deletion and insertion are detectable. Each record links to its predecessor. |
| Epoch Merkle tree | Batch verification. Thousands of hashes combined into a single root per time period. |
| On-chain anchor | External verification. The Merkle root is stored in a blockchain transaction. Anyone can verify. |

A solo practitioner uses the first two layers (free, no external dependencies). A team uses three. A blockchain-enabled network uses all four. The record format is the same at every level — only the verification depth changes.

### Reasoning State as Verified Memory

LLM reasoning state is text. Unlike CPU register state (opaque binary), an LLM's chain of thought is expressed in the same medium the memory store uses. There is no impedance mismatch between what the model is thinking and what the persistence layer can store. Therefore: reasoning checkpoints are stored as standard records, sealed into Merkle epochs, and anchored to the blockchain. The same infrastructure handles both facts and reasoning.

What is captured: plan state, progress, rationale, hypotheses, key decisions, context dependencies.

What is not captured: sub-token attention patterns and implicit contextual weighting — aspects of reasoning the model cannot introspect on. This is the irreducible floor shared by all approaches. It is not a comparative disadvantage.

---

## Part VI — Quality Defence

### The Problem

The methodology is model-agnostic by design. This means it is also model-quality-agnostic. A less capable system can produce text that looks like rigorous falsification — syntactically correct P-Pass structure, plausible constraint classifications, convincing epistemic flags — without any genuine adversarial reasoning behind it. The first draft and the final draft are the same thing wearing different clothes.

The formal model (Section 2.1, property 4) already establishes that when detection probability *p* approaches zero, no number of passes produces corroboration. The persistence layer makes this worse, not better: it faithfully stores reasoning checkpoints that are actually just plausible-sounding text. The verification chain proves the record is untampered — it says nothing about whether the content was worth recording.

### What the Verification Chain Proves and Does Not Prove

| Proves | Does not prove |
|---|---|
| WHO recorded it (source attribution) | Whether the reasoning was genuine |
| WHAT was recorded (content integrity) | Whether the conclusion was correct |
| WHEN it was recorded (temporal ordering) | Whether the P-Pass was substantive or performative |
| That the record is UNTAMPERED | That the record was worth writing |

### The Multi-Layer Defence

No single layer solves this. The defence is architecturally distributed:

1. **Attribution and reputation.** Every record has a source. A consuming system can weight by source. If a particular model instance consistently produces records that do not survive cross-verification, that is a track record. Trust engines that implement earned reputation (not declared competence) provide the judgement layer.

2. **Cross-agent falsification.** Agent A captures a reasoning checkpoint. Agent B independently verifies it. The verification result is itself a record. Over time, agents that produce reasoning which other agents consistently challenge accumulate evidence of that. The persistence layer stores the evidence; the consuming system acts on it.

3. **Consequence tracking.** Records that lead to downstream failures can be traced back to their source. Over time, this builds an empirical quality signal: not whether the reasoning looked right, but whether it led to outcomes that worked.

### What Cannot Be Solved

You cannot distinguish genuine reasoning captured as text from plausible text that resembles genuine reasoning using only the text. This is a fundamental epistemological limitation, not an engineering gap.

A sufficiently large population of low-quality agents all confirming each other's outputs is the Sybil problem applied to reasoning. It requires external controls — human-gated registration, structural trust constraints — to mitigate. The persistence layer alone has no defence against coordinated low-quality consensus, for the same reason a blockchain cannot prevent people from recording bad transactions, only from tampering with recorded ones.

The honest position: you cannot prevent low-quality reasoning from being produced, but you can make it progressively harder for low-quality reasoning to survive cross-verification. This is the same defence science has used for four hundred years. It is not perfect. Nothing is.

---

## Part VII — Known Limitations

1. **The ground truth problem.** The methodology forces explicit adversarial reasoning but cannot verify that reasoning against reality. A confident hallucination passes its own P-Pass because the model does not know it is wrong. The methodology reduces errors caused by insufficient reasoning; it cannot fix errors caused by incorrect training data.

2. **The calibration problem.** Falsifiability conditions may themselves specify wrong thresholds. Domain expert review is required in safety-critical applications.

3. **Context window decay.** Directive adherence weakens over long sessions. Re-assertion at domain shifts mitigates this. It does not eliminate it.

4. **Model capability dependence.** On a frontier-class model, the P-Pass produces genuine adversarial analysis. On a weaker model, it produces the structure of adversarial analysis without its substance. Treat all outputs from less capable models as preliminary hypotheses requiring independent expert review. The formal model (Section 2.1) quantifies this: when p ≈ 0, no number of passes produces corroboration.

5. **Domain boundary.** The methodology applies to STEM, engineering, and technical design. Applied to aesthetics, ethics, or pure preference, it produces false rigour. The suitability gate prevents this when correctly applied.

6. **No literature anchor.** The falsification process has no explicit test for consistency with published empirical literature. In high-stakes domains, an additional test should be added: does this claim contradict published experimental results?

7. **Single-practitioner validation.** This methodology has been developed and applied by one practitioner across multiple projects. The projects exist and function. Whether the methodology caused better outcomes than alternatives would have produced is not established. There is no counterfactual. The empirical validation framework (below) exists to close this gap.

8. **Persistence dependency.** The version update mechanism and cumulative falsification require persistent memory to function across session boundaries. Without the persistence layer, the feedback loop resets at every session start. The methodology remains valid without persistence — each session applies the full P-Pass independently — but the cumulative knowledge that emerges from repeated falsification over time requires a memory architecture.

9. **Human operator dependency.** The manual constraint bounding described in Part III requires a human operator who understands the problem domain well enough to define effective boundaries. The methodology does not make a novice operator effective — it makes an already-competent operator more effective by providing a structured protocol for the AI side of the collaboration. The human skill is the prerequisite, not the output.

---

## Part VIII — Related Work

Several lines of research address overlapping concerns. None implements the full CDSFL methodology; each addresses a subset of the problem space.

**Constitutional AI** (Bai et al., Anthropic, 2022). Uses self-critique and revision guided by a set of principles to reduce harmful outputs. Similar in spirit to the generation-falsification coupling: the model critiques its own output before presenting it. The key difference is that Constitutional AI targets alignment (reducing harmful or dishonest outputs via RLHF), while CDSFL targets correctness (reducing technically wrong outputs via iterative adversarial testing directed by a human operator). Constitutional AI operates at training time; CDSFL operates at inference time via user-defined directives.

**Self-consistency** (Wang et al., 2022). Samples multiple reasoning paths and selects the most common answer. This is a statistical approach: if several independent chains of thought converge on the same answer, that answer is more likely correct. CDSFL's P-Pass is adversarial rather than statistical — it actively attempts to break a single chain of reasoning rather than sampling multiple chains and voting. Self-consistency also provides no mechanism for constraint classification, epistemic marking, or persistence.

**AI debate** (Irving et al., 2018). Two AI agents argue opposing positions; a human judge selects the winner. This externalises the adversarial function that CDSFL internalises within a single model-operator pair. Debate requires two agents and a judge; CDSFL requires one model and one operator. The trade-off: debate avoids the self-adversary limitation (the model testing its own output) but introduces coordination overhead and the problem of judge competence.

**Chain-of-thought verification** (various, 2023–present). Methods for verifying intermediate reasoning steps in chain-of-thought prompting. Addresses the same concern — is the reasoning genuine or merely plausible? — but typically through automated verification of logical steps rather than through iterative adversarial testing of the conclusion. CDSFL's contribution relative to this line of work is the integration of verification with constraint classification, epistemic marking, human constraint bounding, and persistent verified memory.

**Retrieval-Augmented Generation (RAG)** (Lewis et al., 2020). Grounds model outputs in retrieved documents. Addresses the ground truth problem (Limitation 1) by providing external evidence. Does not address sycophancy, uniform certainty signalling, or adversarial self-testing. RAG and CDSFL are complementary: RAG improves the evidence base; CDSFL improves the reasoning applied to that evidence.

No existing work combines all five components of CDSFL: generation-falsification coupling, formal corroboration model, human constraint bounding, epistemic marking, and persistent verified memory. This is a claim of synthesis, not a claim of novelty for any individual component.

---

## Part IX — Empirical Validation

The gap between stated confidence and demonstrated confidence cannot be closed by further internal iteration. It requires external empirical data.

**Core measurement:** Does methodology-prompted output contain fewer physically impossible, logically incoherent, or commercially unviable claims than unguided output, when evaluated by a domain expert against established ground truth?

**Test design:**
- 90 technical prompts across nine domains (hardware engineering, software architecture, logistics, chemistry, structural engineering, biomedical engineering, industrial design, product engineering, cross-domain systems), 10 per domain
- Control condition: each prompt run with no instruction set
- Experimental condition: each prompt run with the methodology as system prompt
- Evaluation: domain expert reviews outputs blind to condition, rates each factual claim on a four-point scale from established-and-correct to critically-incorrect
- Primary metric: rate of critically incorrect claims per response, control vs experimental

The implementation of this protocol is provided in [`bench/`](bench/).

**Validation gap note:** The test design above describes blind domain-expert evaluation. The testbench implementation in `bench/` uses a three-layer automated heuristic for seeded-fault detection: prompt-echo token filtering (prevents scoring on echoed prompt vocabulary), fault-specific keyword matching (requires domain terms not present in the original prompt), and stance-indicator gating (requires explicit error-identification language). This is a stronger proxy than naive keyword matching but remains a weaker form of evaluation than expert review. The heuristic may produce false negatives (faults detected in language the scorer does not recognise) and has known limitations on terse responses that lack explicit error-identification vocabulary. Manual adjudication of a calibration sample is recommended before headline claims. The testbench demonstrates that the evaluation protocol is mechanically executable; it does not claim equivalence with expert review.

**Estimated cost:** approximately $1.98 at representative frontier model pricing. Well within the budget of any individual researcher.

**Scope:** This test shows whether the methodology reduces critical errors in a frontier-class model on technical tasks across nine STEM domains spanning the boundary described in Part VII. Equivalence across model classes, persistence across full session lengths without re-assertion, and stability across domains not yet represented remain second-phase research questions.

The protocol is published so that anyone can execute it, reproduce or refute the observation, and extend the methodology. If the advantage does not replicate, that is a result, not a failure.

### Extended P-Pass

The standard P-Pass runs all passes within a single context window. For multi-module projects (3+ distinct modules or components with independent constraint sets), this creates two problems: (1) monolithic passes spread attention across all components, reducing detection probability for intra-module faults; (2) later passes in the same context anchor on conclusions from earlier passes, reducing adversarial effectiveness through confirmation bias.

The **Extended P-Pass** addresses both by splitting the 5-pass budget into 4 modular passes + 1 isolated adversarial pass:

- **Passes 1-4 (Modular):** Each scoped to one module or component, falsifying its constraint set, interfaces, and assumptions in isolation. Standard CDSFL rules apply within each pass.
- **Pass 5 (Isolated Adversarial):** MUST run in a fresh context containing ONLY the original work product and an adversarial brief — not the P-Pass analyses from passes 1-4. No prior conclusions are visible. In Claude Code, this means using the Agent tool with a subagent for context isolation. In general LLM usage, start a new conversation. The brief frames the task as independent verification, directing the model to find cross-module interface errors, conflicting assumptions, and emergent contradictions.

The theoretical basis is differential detection probability. Modular passes have higher *p* for intra-module faults (focused attention) but lower *p* for cross-module faults (can't see what's between modules). The isolated adversarial pass inverts this profile. For a fault distribution where the majority of errors are intra-module — which empirical evidence from safety-critical industries suggests is the case — the hybrid should outperform either pure strategy.

The adversarial pass terminates when: all HARD constraint assumptions have been tested and found sound, remaining findings are below the real-world-consequence threshold, and further passes would produce no new failures, only alternative preferences. The threshold test: would this finding, if missed, cause a real-world failure, violation, or unsafe condition? If not, it is below threshold. This prevents the adversarial pass from degenerating into unbounded nitpicking while ensuring genuine issues are not dismissed prematurely.

When NOT to use Extended P-Pass: single-module projects (use standard 5-pass), projects where modules share so much state that isolating them is artificial, or when the total work product is small enough that monolithic passes achieve adequate depth (rough guide: under ~500 lines or ~2000 words).

The testbench supports `--mode extended` for comparative data against the standard P-Pass on the same seeded-fault tasks. **Implementation note:** the current testbench implements final-pass context isolation only — iterative passes followed by one isolated adversarial pass without prior P-Pass conclusions. It does not implement the full module-scoped decomposition described above, which would require per-task module maps that the current task schema does not provide. The testbench therefore tests whether context isolation on the final pass adds detection value, not whether module-scoped pass decomposition does. The full 4+1 module-scoped protocol remains the specification; the testbench evaluates one component of it. The protocol mirrors established practice in safety-critical engineering (IEC 61508 independent assessment, DO-178C independent verification), where the verification team must not have access to the design team's analysis. Whether context isolation in LLMs achieves the same cognitive independence as organisational independence in human teams is an open empirical question that the testbench is designed to answer.

---

## Part X — Worked Examples

Each of the following projects was built using this methodology. They are linked here as evidence of the methodology in practice, not as claims of superiority over alternative approaches. Each repo has its own documentation and stands independently.

| Project | What it is | Repo |
|---|---|---|
| **Project Genesis** | Trust-mediated labour market for mixed human-AI populations. Constitutional engineering, governance as falsifiable code, Popperian design methodology applied to social architecture. | [Project_Genesis](https://github.com/jebus197/Project_Genesis) |
| **Open Brain** | Persistent, cross-agent, cross-session verified memory for AI systems. The persistence and verification layer described in Part V of this document. | [OpenBrain](https://github.com/jebus197/OpenBrain) |
---

## Invitation to Falsify

This document practises what it describes. Every claim made here is presented as a falsifiable assertion:

- The claim that the generation-falsification coupling reduces errors is testable by the empirical validation protocol in Part IX.
- The claim that constraint classification prevents implicit trade-offs is testable by adversarial prompt design.
- The claim that the verification chain detects tampering is testable by attempting to tamper with verified records.
- The claim that manual constraint bounding improves outcomes is testable by comparing operator-bounded sessions against unbounded sessions on equivalent tasks.
- The claim that the quality defence makes low-quality reasoning harder to sustain is testable by deploying the methodology across agents of varying capability and measuring cross-verification outcomes.
- The formal corroboration model C(n) = 1 − (1 − p)ⁿ is testable by measuring actual detection rates across multiple passes on seeded-fault benchmarks.
- The corroboration model itself — the application of geometric survival mathematics to LLM self-falsification — may be the wrong model entirely. If a fundamentally different framework predicts P-Pass outcomes more accurately, this one should be replaced. The methodology's validity does not depend on this specific equation.

If any of these claims do not survive external testing, the methodology is improved by the correction. The commitment is to the process of falsification, not to any particular outcome.

---

*Constraint-Driven Synthesis and Falsification Loop (CDSFL) v1.0. Derived by iterative Popperian falsification. March 2026.*
