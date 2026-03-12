# Constraint Engineering

**A working methodology for AI-augmented engineering, and a guide to navigating this body of work.**

---

## What This Document Is

This is the methodology I use. It governs how I work with AI systems on complex engineering tasks. Everything else in my repositories — the projects, the architectures, the governance systems — emerged from applying this methodology over a sustained period of work across multiple domains.

This document is not a manifesto. It is a description of practice. If anything here is wrong, the methodology itself demands that it be identified, documented, and corrected.

---

## How to Read This Repository

This repo sits at the top of my public work. The projects listed at the end are worked examples — each one was built using the methodology described here. They are not subordinate to this document; they stand in their own right. But they share a common engineering discipline, and this document explains what that discipline is.

If you are a researcher, engineer, or practitioner who works with AI systems and has encountered the same problems this methodology addresses — sycophantic agreement, confident hallucination, reasoning that simulates rigour without producing it — you may find something useful here. If not, this work was probably not built for you.

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

The P-Pass (Popperian falsification pass) is the load-bearing mechanism. It operationalises Karl Popper's principle of falsification as an iterative engineering process:

1. **Identify the problem.**
2. **Generate the best available solution.**
3. **Attempt to destroy it.** This is iterative, not observational. Actively construct scenarios designed to break the claim. Check edge cases. Examine the claim from the perspective of an opponent.
4. **Fix what breaks.**
5. **Attempt to break the fix.**
6. **Continue until the solution cannot be broken further without leaving the defined scope.**

A P-Pass that finds no failures on the first attempt is suspect. Repeat with increased adversarial rigour before accepting a clean result.

Deferral is acceptable only when the fix is genuinely outside the current scope. When deferred, the deferral is stated explicitly with the conditions under which it becomes actionable.

**Suitability gate:** before running the P-Pass, determine whether the task involves claims where being wrong produces a non-functional, physically impossible, legally invalid, or unsafe outcome. If yes, run the full loop. If the task is only partially falsifiable, apply the loop to those components and state the boundary. If the task is not falsifiable — aesthetics, ethics, pure preference — say so and apply judgement. Do not produce false rigour. A schema applied to a task where falsifiability is structurally absent produces the appearance of methodological discipline without its substance. This is more dangerous than honest uncertainty.

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

## Part III — Persistence and Verification

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

## Part IV — Quality Defence

### The Problem

The methodology is model-agnostic by design. This means it is also model-quality-agnostic. A less capable system can produce text that looks like rigorous falsification — syntactically correct P-Pass structure, plausible constraint classifications, convincing epistemic flags — without any genuine adversarial reasoning behind it. The first draft and the final draft are the same thing wearing different clothes.

The persistence layer makes this worse, not better. If a low-quality model captures reasoning checkpoints that are actually just plausible-sounding text, the persistence layer stores them faithfully. The verification chain proves the record is untampered — it says nothing about whether the content was worth recording.

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

## Part V — Known Limitations

1. **The ground truth problem.** The methodology forces explicit adversarial reasoning but cannot verify that reasoning against reality. A confident hallucination passes its own P-Pass because the model does not know it is wrong. The methodology reduces errors caused by insufficient reasoning; it cannot fix errors caused by incorrect training data.

2. **The calibration problem.** Falsifiability conditions may themselves specify wrong thresholds. Domain expert review is required in safety-critical applications.

3. **Context window decay.** Directive adherence weakens over long sessions. Re-assertion at domain shifts mitigates this. It does not eliminate it.

4. **Model capability dependence.** On a frontier-class model, the P-Pass produces genuine adversarial analysis. On a weaker model, it produces the structure of adversarial analysis without its substance. Treat all outputs from less capable models as preliminary hypotheses requiring independent expert review.

5. **Domain boundary.** The methodology applies to STEM, engineering, and technical design. Applied to aesthetics, ethics, or pure preference, it produces false rigour. The suitability gate prevents this when correctly applied.

6. **No literature anchor.** The falsification process has no explicit test for consistency with published empirical literature. In high-stakes domains, an additional test should be added: does this claim contradict published experimental results?

7. **Single-practitioner validation.** This methodology has been developed and applied by one practitioner across multiple projects. The projects exist and function. Whether the methodology caused better outcomes than alternatives would have produced is not established. There is no counterfactual. The empirical validation framework (below) exists to close this gap.

8. **Persistence dependency.** The version update mechanism and cumulative falsification require persistent memory to function across session boundaries. Without the persistence layer, the feedback loop resets at every session start. The methodology remains valid without persistence — each session applies the full P-Pass independently — but the cumulative knowledge that emerges from repeated falsification over time requires a memory architecture.

---

## Part VI — Empirical Validation

The gap between stated confidence and demonstrated confidence cannot be closed by further internal iteration. It requires external empirical data.

**Core measurement:** Does methodology-prompted output contain fewer physically impossible, logically incoherent, or commercially unviable claims than unguided output, when evaluated by a domain expert against established ground truth?

**Test design:**
- 30 technical prompts across three domains (hardware engineering, software architecture, logistics), 10 per domain
- Control condition: each prompt run with no instruction set
- Experimental condition: each prompt run with the methodology as system prompt
- Evaluation: domain expert reviews outputs blind to condition, rates each factual claim on a four-point scale from established-and-correct to critically-incorrect
- Primary metric: rate of critically incorrect claims per response, control vs experimental

**Estimated cost:** approximately $0.66 at representative frontier model pricing. Well within the budget of any individual researcher.

**Scope:** This test shows whether the methodology reduces critical errors in a frontier-class model on technical tasks in three specific domains. Equivalence across model classes, stability across all domains, and persistence across full session lengths without re-assertion are second-phase research questions.

The protocol is published so that anyone can execute it, reproduce or refute the observation, and extend the methodology. If the advantage does not replicate, that is a result, not a failure.

---

## Part VII — Worked Examples

Each of the following projects was built using this methodology. They are linked here as evidence of the methodology in practice, not as claims of superiority over alternative approaches. Each repo has its own documentation and stands independently.

| Project | What it is | Repo |
|---|---|---|
| **Project Genesis** | Trust-mediated labour market for mixed human-AI populations. Constitutional engineering, governance as falsifiable code, Popperian design methodology applied to social architecture. | [Project_Genesis](https://github.com/jebus197/Project_Genesis) |
| **Open Brain** | Persistent, cross-agent, cross-session verified memory for AI systems. The persistence and verification layer described in Part III of this document. | [OpenBrain](https://github.com/jebus197/OpenBrain) |
| **Aeigis** | Threat modelling and security architecture. | [Aeigis](https://github.com/jebus197/Aeigis) |
| **CANDELA** | Model-agnostic governance framework for AI output verification. Directive enforcement and ledger anchoring. | [CANDELA](https://github.com/jebus197/CANDELA) |

---

## Invitation to Falsify

This document practises what it describes. Every claim made here is presented as a falsifiable assertion:

- The claim that the generation-falsification coupling reduces errors is testable by the empirical validation protocol in Part VI.
- The claim that constraint classification prevents implicit trade-offs is testable by adversarial prompt design.
- The claim that the verification chain detects tampering is testable by attempting to tamper with verified records.
- The claim that the quality defence makes low-quality reasoning harder to sustain is testable by deploying the methodology across agents of varying capability and measuring cross-verification outcomes.

If any of these claims do not survive external testing, the methodology is improved by the correction. The commitment is to the process of falsification, not to any particular outcome.

---

*Derived by iterative Popperian falsification. March 2026.*
