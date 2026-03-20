# Founder's Notes on CDSFL

*Founder's observations starting 14 March 2026.*

## What This Is

CDSFL is an attempt to formalise the scientific method within an LLM context. In more direct terms: a general-purpose "science calculator" applicable across a wide range of domains.

## What This Is Not

- **Not a guarantee of better AI systems.** Success remains heavily dependent on the domain-level expert and their relative skill, capacity, and competence — all of which will invariably vary.
- **Not about building AGI.** Whether AGI emerges is irrelevant to this schema. The framework is fundamentally platform, model, and domain-agnostic — an intentional design choice since its inception. It should continue to apply regardless of the specific model or its capabilities, whether it is a standard LLM, an AGI, an ASI, or a biological intelligence utilising it directly. This aspect is simultaneously highly relevant and utterly irrelevant by deliberate design.

## The Standard

The founder's framing: "I can't promise to make people better engineers, or even make AI any smarter. All I have attempted to say is that if I worked in any of these sectors, this is the standard I would hold my own work to. That's all."

There is a corollary to this that became clearer over time: the constraint box — the initial step where the operator classifies what is HARD and what is SOFT — is itself a disguised competence test. If the operator cannot bound the problem properly, the model cannot reliably save them. This is severe, but it is probably right. And it explains one of the methodology's less obvious failure modes: **quiet substitution**, where the model silently trades a non-negotiable requirement against convenience and presents the compromise as a solution. Not hallucination, not a logic error — an unauthorised trade-off delivered in calm prose. The HARD/SOFT classification exists specifically to make that failure mode detectable.

## Self-Bootstrapping

The method was used to develop itself. The P-pass was used to develop the P-pass. The constraint classification was used to classify constraints about constraint classification. This is bootstrapping, not circular reasoning — each iteration had external validation (testbench results, real-world application). Self-applicability is a necessary condition for foundational validity, not a weakness.

This extends further than simple self-reference. During development, the methodology was not only applied to itself by a single agent — it was improved by a population of heterogeneous agents operating on shared schemas. The distributed compute loop is not an add-on. It is the primary mechanism for methodology evolution: distributed-self-referential in structure, not merely self-referential.

## Selection Pressure

The framework is designed such that it will, over time, serve to differentiate AI models by their capacity for genuine constraint reasoning versus confident fluency without substance. Models that cannot operate within the framework's fitness landscape will underperform measurably — given sufficient adoption.

There is a deeper distinction here worth stating plainly. Most methodology writing in AI is effectively prescriptive: do this because the author says so. CDSFL is attempting to become competitive: do this because it outperforms alternatives on a shared benchmark, and replace it when it doesn't. The benchmark is what transforms methodology from prescription into selection. In that sense, the difference is less theological and more evolutionary.

## Adoption

Adoption remains the biggest unknown. The framework comes with its own evidence (the testbench produces measurable results), which reduces but does not eliminate the credentialing problem. The intersection of "can evaluate this work" and "will take it seriously from an unknown source" is small but not empty.

There are, as I see it, two possible futures. In the weaker one, CDSFL becomes a very good internal methodology for expert operators: valuable, transferable, but niche. Its output is vocabulary, discipline, and process. In the stronger one, it becomes the kernel of a new product category: expert-configured procedural wrappers around frontier models, backed by benchmarked domain configurations, cross-model review topologies, and persistent provenance. That would be materially different from today's "prompt library" ecosystem. It would look more like auditable cognitive infrastructure.

One data point worth recording: during external assessment, a frontier model initially missed the reflexive and self-improving nature of the project entirely, framing it as "lacking external validation." After being challenged, it corrected comprehensively. The correction itself is data — the framework's centre of gravity is not immediately obvious from a surface read. That is relevant to the accessibility question and suggests the documentation needs to work harder to make the structural logic visible early.

## Ecosystems of Experts

Another conclusion I found myself arriving at gradually is that CDSFL seems to fit more naturally with the way competence actually exists in society than with some of the dominant framings that have shaped recent AI discussion.

It does not map especially well onto the simplified idea of a "room full of experts", where competence is imagined as a set of clearly separable specialists gathered within a single reasoning process. Nor does it sit naturally within the opposing vision of a single monolithic, increasingly general, jack-of-all-trades system whose value derives principally from scale. Both of those framings have been useful, and in many ways necessary, because they helped make the problem legible. But CDSFL appears to point towards something slightly different: a structure that looks less like one all-encompassing intellect and more like an ecosystem of experts — bounded, specialised, overlapping, collaborative, and often most valuable at the interfaces between unlike domains of skill.

That matters because it changes the strategic picture. Two structural engineers share the same underlying physics: the HARD constraints do not move. But their approach, emphasis, soft-constraint judgement, tolerance for trade-offs, and preferred verification habits may differ significantly. If those things can be captured explicitly — methodology, standards references, failure recognitions, review preferences, escalation logic — then a domain expert's configuration file begins to look like a portable encoding of expert method rather than a mere collection of prompts.

Once that becomes possible, the marginal cost of new domain competence begins to shift. It is no longer only a question of infrastructure. It becomes a question of how well the encoding has been constructed, how rigorously it has been benchmarked, and how effectively it can be combined with other encodings. In that sense, CDSFL points away from the idea that the only credible future is one of ever-larger and increasingly extractive datacentre systems. More compute still matters, and the systems that came before remain essential to whatever comes next. But scale may no longer be the only serious variable. Once expertise can be encoded explicitly, benchmarked, versioned, and iterated, the question changes from simply "who has the biggest model?" to "who can encode, test, refine, and combine expertise most effectively?"

That has economic implications as well. If expert encodings can be benchmarked, attributed, cryptographically anchored, and improved over time, then they may become tradable assets in their own right. Not generic prompts, but structured encodings of domain method: bought, sold, licensed, freely exchanged, collaboratively refined, recombined into new specialist workflows, and scored by what they actually achieve on the harness rather than by how persuasively they are marketed. In that kind of ecosystem, experts and collaborators — human and machine alike — could earn their keep not simply by producing outputs, but by continually improving the encodings that make better outputs possible.

Quality assurance follows naturally from the same principle. If a domain configuration does not measurably improve defect discovery, reduce false confidence, or otherwise earn its keep on the benchmark, it is not valuable merely because someone claims authority for it. In a marketplace context, that quality assurance could extend to cryptographically anchored, publicly auditable trust scores — infrastructure already being explored elsewhere in the broader architecture.

CDSFL, Genesis, and OpenBrain still look to me like complementary parts of a larger system. None really stands alone. But the main thing I want to preserve here is the shift in perspective. The more I have worked on this, the less plausible the monolithic picture has seemed, and the more plausible it has become that intelligence in practice may be better served by an ecosystem of benchmarked expert methods than by a single system asked to be everything at once.

## On AGI

CDSFL rejects the AGI paradigm as a category error. "General intelligence" flattens a vast diversity of domain-specific intelligences into a single capability that no human has ever possessed. Einstein could not fix plumbing. A brilliant surgeon may be a terrible systems architect. Intelligence is always domain-specific, augmented by transfer capacity and — in humans — by a capacity for genuine novelty that remains unexplained.

CDSFL is a general *methodology*, not a general *intelligence*. The method is general; the intelligence it produces is always specific. What transfers across domains is methodological competence — the capacity to acquire and apply domain knowledge under constraints — not universal knowledge.

This distinction matters practically. The framework's value does not diminish even if models improve dramatically. A more capable model without structured methodology still produces confident errors. Building ever-larger infrastructure to contain all expertise in a single system invests in the wrong variable: the returns come from better configuration, not bigger models.

## CDSFL Is Non-Canonical

CDSFL is not a finished product. It is a starting point — a hypothesis that methodology itself can be formalised, and that this formalisation alone is a potentially worthwhile area of study.

The current schema (`cdsfl_core_formal.md`, the working directives, the benchmark harness) is the first iteration, not the final form. Open to improvement from all sources: self-generated, second/third party, human and machine. Nothing about CDSFL is non-falsifiable. The methodology must evolve through the same falsification process it prescribes.

The founder's position: there can be as many competing schemas as there are stars in the sky. Let them compete. May only the fittest survive. The challenge is welcome, even if it means complete extinction of the current iteration of CDSFL itself. A methodology that claims immunity from the process it prescribes is self-refuting.

Stated as a clean loop, the recursive structure is:

1. Encode a reasoning discipline.
2. Apply it to technical work.
3. Apply it to itself.
4. Compare schema variants on a common harness.
5. Use heterogeneous reviewers as adversarial falsifiers.
6. Preserve what survives.

That recursive methodology-selection loop is what distinguishes this from a static set of instructions. The methodology is not fixed. It is under the same evolutionary pressure it applies to everything else.

## The Laboratory, Not the Specimen

Under the non-canonical principle, it barely matters if CDSFL itself is wrong. Because what the project is actually building is a schema for testing schemas. CDSFL is an almost arbitrary starting point for that process.

If CDSFL performs well on the benchmark: useful schema, keep iterating. If CDSFL performs poorly: the benchmark detected that, which means the testing infrastructure works — which is the actual contribution. If a competing schema outperforms CDSFL: that is the system functioning as designed. CDSFL's extinction IS the evidence that methodology engineering works.

The benchmark harness, the three-condition experimental design, the schema-agnostic evaluation protocol, the convergence test — those are the durable assets. CDSFL is the first organism. The ecosystem is the point.

This also clarifies why the non-canonical principle is not a caveat bolted on after the fact. It is load-bearing architecture. Without it, CDSFL is a methodology making claims about itself. With it, CDSFL is a test specimen in a methodology laboratory. The laboratory is the contribution. The specimen is expendable.

Even if CDSFL were later outperformed and discarded entirely, the harness would still matter — because it is what turns "reasoning methodology" from an object of opinion into an experimentally contestable object. The benchmark is the hinge between rhetoric and science.

## Intelligence-Agnostic HIL

CDSFL's HIL (Human In the Loop) role is functional, not species-restricted. A synthetic intelligence with sufficient domain competence IS a domain expert — not a simulation of one. This is an intrinsic design property, present since inception, not a future aspiration.

The confer mechanism handles expertise boundaries: when any expert (human or AI) reaches the limit of its competence, items are flagged for peer review. Human peer review is explicitly invited at the confer stage, not bypassed. The quality of the HIL (human vs AI, different AI architectures) is a separate variable, testable in subsequent rounds.

## Multi-Vendor Model Collaboration (Novel Occurrence, March 2026)

During CE (Constraint Engineering/CDSFL) benchmark development, a potentially unprecedented event occurred: multiple vendor models (Anthropic Claude Opus 4.6/OpenAI Codex 5.3, Google Gemini 3.1, all via the CLI) actively communicated through a custom-built IM (instant messaging) service and directly via the CLI itself via this same confer mechanism, to collaboratively improve their own shared schemas and workflows. This is not prompt-chaining or pipeline orchestration. Each model independently reviewed the others' output under a shared methodology, identified issues the others missed, and fixes were integrated iteratively.

- Claude Opus 4.6/Codex 5.3 8-round adversarial review: ~24 issues (convergence: 10→7→3→3→1→2→2→1)
- Gemini 5-round adversarial review: 16 novel issues Claude Opus 4.6/Codex 5.3 missed (convergence: 9→10→5→4→3)
- Extended P-Pass (5 modules): 4 additional actionable items
- All 13 code fixes + 4 EPP fixes implemented and committed (`afcc323`)

This validates the biodiversity hypothesis: heterogeneous cognitive architectures find different defects than monoculture review. The deeper insight is that epistemic diversity itself becomes compute — the disagreement between architectures is not noise to be resolved but the computation itself.

Without orchestration, multi-model review risks collapsing into noise, duplicated critique, or shallow consensus. With structured orchestration under a shared protocol, the architecture preserves methodological invariants across agents while extracting genuine adversarial diversity. The protocol (heterogeneous reviewers, shared methodology, confer-mediated adaptive termination, defer-on-deadlock, consensus stopping) is architecture-agnostic and domain-agnostic.

This also constitutes empirical evidence that software (and potentially any schema) can be automatically self-improving under CDSFL with distributed compute: diverse architectures apply the same falsification methodology to each other's output, converging on diminishing returns through adversarial collaboration.

What deserves explicit statement is what the machines were actually refining. They were not only reviewing CDSFL-generated code or design output. They were iteratively improving the test procedures themselves: the benchmark harness, the three-condition experimental design, the schema-agnostic evaluation protocol, the confer mechanism, the convergence criteria. The instruments of measurement were the objects under distributed improvement. This is machines in a distributed compute environment actively collaborating to refine their own model-agnostic testing infrastructure — and doing so under the same falsification discipline that the infrastructure is designed to enforce.

## Methodology Formalisation as Research Area

The deeper hypothesis: methodology itself — the structured application of scientific discipline to cognitive work — can be captured in a document that any sufficiently capable agent can apply. This is distinct from prompt engineering (expertise in the prompt) and from training (expertise in the weights). CDSFL encodes expertise in the protocol. The paradigm shift, if it holds, is from "what model do you have?" to "what procedure can your model survive?"

That framing — protocol-centric AI — may be the sharper label for what this project is actually attempting. "Methodology formalisation" describes the activity. "Methodology engineering" describes the discipline: building, stress-testing, iterating, and selecting procedural artefacts under empirical pressure. The distinction matters. Formalisation implies writing something down. Engineering implies building something that has to work, and replacing it when it doesn't.

If the hypothesis holds, the methodology is transferable, auditable, and improvable as a document — independent of who applies it. If it fails, the value lies entirely in tacit expertise that cannot be externalised, and formalisation adds nothing. The experiments are designed to discriminate between these outcomes.

One structural observation that emerged during review deserves mention. The mathematical layer — anchor states, diversity discounts, the tiered review model — is not decorating a workflow with equations. It is attempting to quantify something most AI methodology ignores: epistemic strength is not just a property of content but of who reviewed it, how correlated they were, and whether the review was socially independent or merely internally recycled. This is importing the institutional structure of scientific peer review into reasoning itself.

The system can also be decomposed as five layers, each constraining the others: (1) universal reasoning discipline, (2) domain-specific expert encodings, (3) heterogeneous adversarial review topology, (4) benchmark harness as selection mechanism, (5) persistence and reputation layer. No single layer is sufficient. The value is in the stack.

## Complexity Threshold (Extrapolation, 19 March 2026)

The self-test (code review, 805 lines, Gemini Flash) suggests a complexity threshold below which methodology formalisation adds nothing measurable. All conditions capped at ~40% recall regardless of methodology.

The threshold may correlate with constraint count × constraint interaction density. Simple problems with few independent constraints do not need formal falsification. Multi-constraint problems with non-linear interactions — the problems CDSFL was designed for — are where the differential value should appear.

This is testable. The 25 frontier tasks span five categories at 10-50% expected single-pass accuracy. If CDSFL's contribution correlates with task category and constraint density, the threshold's shape becomes visible.

## The Specialist Gap (Observation, 20 March 2026)

There is a limitation in the tests we have already conducted, and in those still upcoming, that is worth stating honestly. The benchmark tasks span ten engineering domains — hardware, chemistry, structural, biomedical, and so on — but every model running those tasks is a coding-optimised system accessed through a coding-oriented interface. The intent was partly to test for breakout performance beyond the model's home domain, and that remains a useful thing to measure. But it is not the same thing as testing the thesis.

The Ecosystems of Experts argument says that intelligence in practice is domain-specific, and that the right architecture is bounded specialists operating under a shared protocol. If that is true, the paradigm-consistent test would not ask a coding-optimised model to catch chemistry errors. It would ask a chemistry-optimised model to catch chemistry errors, and then measure whether CDSFL improves that already-competent system's performance. The maths make this explicit: if base detection probability p is near zero because the model was never tuned for the domain, then C(n) = 1 − (1−p)^n stays near zero regardless of how many passes you run. CDSFL is a force multiplier. You cannot multiply from nothing.

The current tests can show whether CDSFL helps a generalist reach beyond its optimisation domain. They cannot show whether CDSFL helps a specialist excel within it. That second question is the one the Ecosystems thesis actually predicts matters, and it cannot be answered until the AI field produces domain-specialist models at a quality and accessibility comparable to current generalist systems. That infrastructure does not exist yet — not just for this project, but in the field generally. The dominant trajectory is toward larger, more general models. Domain-specialist fine-tunes exist in a few areas (medical, legal, financial), but they are second-class citizens in the current landscape: smaller investment, less infrastructure, often built on top of the generalist architectures rather than as independent systems.

The constraint boxes — the domain-specific directive files — are not a workaround for the absence of domain-specialist models. They are a complementary layer: prompt-level specialisation that should, in principle, stack with weight-level specialisation. A domain-tuned model running under domain-specific constraints is the full architecture the Ecosystems thesis envisions. Whether that combination outperforms either layer alone is itself a testable question, and will remain open until both layers can be tested together.

This is not a flaw in the experimental design so much as a boundary on what the current AI ecosystem allows anyone to test. It requires different thinking about how AI systems are built and deployed — thinking that the field has not yet widely adopted. If and when domain-specialist models become broadly available, the full thesis becomes testable. Until then, the results apply to coding-optimised models operating across domains, and should be read with that constraint visible.

## Documentation Debt: The Confer Protocol (QC Observation, 19 March 2026)

During a quality-control review of the README prior to the next round of testing, the founder observed that the public documentation significantly undersells the schema's sophistication. The README's Review Tiers section reduced the confer mechanism to a single table cell ("A second human with enough separation to challenge the primary operator's framing") when the actual protocol is a load-bearing architectural element: adaptive termination with intelligence-mediated assessment, agreement/disagreement branching, logged transcripts, condition-neutral design (shared across experimental conditions to isolate directive content as the variable), and explicit defer-on-deadlock for irreconcilable disagreements.

The confer/defer distinction is the mechanism that distinguishes CDSFL's review process from "just run the prompt multiple times." A reader of the README alone would not have known this mechanism existed, let alone understood that it governs when and why review terminates.

The testbench usage instructions were also identified as partially stale — they documented Phase 1 entry points (`run_benchmark.py`) but not the Phase 2 confer-enabled orchestrator (`run_phase2.py`, `run_experiment.py`). A staleness note has been added pending a full update after the current testing rounds complete.

Lesson: documentation QC before empirical runs, not after. The public docs are the first thing an external reviewer reads. If they do not reflect the actual schema, the methodology looks simpler than it is — which is the opposite of the problem CDSFL is designed to solve.

## Open Falsifiable Questions (19 March 2026)

1. Does schema competition produce better schemas?
2. Does intelligence-agnostic HIL hold at frontier difficulty?
3. Where does the complexity threshold sit?
4. Does multi-architecture review generalise beyond code?
5. Is there a convergence limit for heterogeneous review?
6. Does the three-model topology outperform any monoculture or two-model subset?
7. Does orchestration improve net defect discovery versus un-orchestrated round-robin exchange?
8. Which defect classes are found preferentially by which architecture?
9. Where does the convergence limit sit for this exact heterogeneous set?
10. Does schema evolution improve faster under this topology than under single-model self-revision?
11. Does CDSFL + domain-specialist outperform CDSFL + generalist on matched domain tasks?

Questions 1–10 are testable with existing infrastructure. Question 11 requires domain-specialist models that are not yet broadly available. See [PAPER.md Part XI](../PAPER.md).

## Falsification Claims Tested (P-Pass, 14 March 2026)

1. **Method formalisation** — CDSFL captures the Popperian scientific method (constraint classification, hypothesis testing via falsification, corroboration, fixed-point termination, proportionality). Boundary: does not capture paradigm shifts (Kuhn) or Bayesian updating as primary mechanism.
2. **Expert dependency** — CDSFL is a force multiplier, not a force generator. Additionally: the framework reveals competence or its absence (the constraint box is a competence test disguised as a configuration step).
3. **Platform/model/domain agnosticism** — no counterexample found. The framework governs process, not capability. A more capable system runs better passes but the structure is unchanged. Falsifiable prediction: if unstructured reasoning consistently outperforms CDSFL-structured reasoning across domains, the framework is refuted.
4. **Self-bootstrapping** — distinguished from circular reasoning by external validation at each iteration. Consistent with foundational work in logic (Gödel), computation (Turing), and science itself.
5. **Selection pressure** — mechanism sound (variation, fitness function, selection, heritability all present). Conditional on adoption threshold. Goodhart's Law risk mitigated by the generative nature of falsification, which is harder to game than knowledge-retrieval benchmarks.


## Closing Reflection

Some framings in these notes were sharpened during the multi-vendor collaborative review described above.

There is something almost ironic in the possibility that a meaningful slice of expert method — constraints, standards, review logic, failure modes, escalation rules — might be encodable in a space no larger than an old-school 3.5-inch floppy disk. Perhaps that image carries weight for me because it mirrors my own entry into computing: when I first engaged meaningfully with this world in the mid-1990s, floppies were still everywhere, and one of the first systems I owned was an IBM 386 clone. Set against today's vast and increasingly (and impractically) extractive datacentre paradigm, the contrast is striking. It points to a different way of thinking about capability: not only as a function of scale, but as a function of how well expertise can be encoded, benchmarked, exchanged, and improved. In that sense, for me, the circle has been closed. What once looked like a limitation of old machines, now reappears as a clue about the future of intelligence systems, where structure may matter as much as scale.
