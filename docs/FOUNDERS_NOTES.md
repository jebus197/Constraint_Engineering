# CDSFL: Constraint-Driven Synthesis and Falsification

## Founder's Notes

*Founder's observations, recorded chronologically from 14 March 2026 onwards. Undated sections reflect foundational principles established at the project's inception. Dated sections record observations as they emerged during development and testing.*

*The founder's experimental journal — contemporaneous notes kept during development and testing — is preserved unedited in [`experimental_notes/`](experimental_notes/). This document is the curated interpretive account.*

## What This Is

CDSFL is an attempt to formalise the scientific method within an LLM context. In more direct terms: a general-purpose "science calculator" applicable across a wide range of domains.

## What This Is Not

- **Not a guarantee of better AI systems.** Success remains heavily dependent on the domain-level expert and their relative skill, capacity, and competence — all of which will invariably vary.
- **Not about building AGI.** Whether AGI emerges is irrelevant to this schema. The framework is fundamentally platform, model, and domain-agnostic — an intentional design choice since its inception. It should continue to apply regardless of the specific model or its capabilities, whether it is a standard LLM, an AGI, an ASI, or a biological intelligence utilising it directly. This aspect is simultaneously highly relevant and utterly irrelevant by deliberate design.

## The Standard

The founder's framing: "I can't promise to make people better engineers, or even make AI any smarter. All I have attempted to say is that if I worked in any of these sectors, this is the standard I would hold my own work to. That's all."

There is a corollary to this that became clearer over time: the constraint box — the initial step where the operator classifies what is HARD and what is SOFT — is itself a disguised competence test. If the operator cannot bound the problem properly, the model cannot reliably save them. This is severe, but it is probably right. And it explains one of the methodology's less obvious failure modes: **quiet substitution**, where the model silently trades a non-negotiable requirement against convenience and presents the compromise as a solution. Not hallucination, not a logic error — an unauthorised trade-off delivered in calm prose. The HARD/SOFT classification exists specifically to make that failure mode detectable.

## Self-Bootstrapping

The method was used to develop itself. The P-pass was used to develop the P-pass. The constraint classification was used to classify constraints about constraint classification. This is bootstrapping, not circular reasoning — each iteration had empirical testing against measurable outcomes (testbench results, real-world application). Self-applicability is a necessary condition for foundational validity, not a weakness.

This extends further than simple self-reference. During development, the methodology was not only applied to itself by a single agent — it was improved by a population of heterogeneous agents operating on shared schemas. The distributed compute loop is not an add-on. It is the primary mechanism for methodology evolution: distributed-self-referential in structure, not merely self-referential.

## Selection Pressure

The framework is designed such that it will, over time, serve to differentiate AI models by their capacity for genuine constraint reasoning versus confident fluency without substance. Models that cannot operate within the framework's fitness landscape will underperform measurably — given sufficient adoption.

There is a deeper distinction here worth stating plainly. Most methodology writing in AI is effectively prescriptive: do this because the author says so. CDSFL is attempting to become competitive: do this because it outperforms alternatives on a shared benchmark, and replace it when it doesn't. The benchmark is what transforms methodology from prescription into selection. In that sense, the difference is less theological and more evolutionary.

## Adoption

Adoption remains the biggest unknown. The framework comes with its own evidence (the testbench produces measurable results), which reduces but does not eliminate the credentialing problem. The intersection of "can evaluate this work" and "will take it seriously from an unknown source" is small but not empty.

There are, as I see it, two possible futures. In the weaker one, CDSFL becomes a very good internal methodology for expert operators: valuable, transferable, but niche. Its output is vocabulary, discipline, and process. In the stronger one, it becomes the kernel of a new product category: expert-configured procedural wrappers around frontier models, backed by benchmarked domain configurations, cross-model review topologies, and persistent provenance. That would be materially different from today's "prompt library" ecosystem. It would look more like auditable cognitive infrastructure.
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

The benchmark harness, the four-condition 2x2 factorial design (Control, HIL, CDSFL, CDSFL+HIL), the schema-agnostic evaluation protocol, the convergence test — those are the durable assets. CDSFL is the first organism. The ecosystem is the point.

This also clarifies why the non-canonical principle is not a caveat bolted on after the fact. It is load-bearing architecture. Without it, CDSFL is a methodology making claims about itself. With it, CDSFL is a test specimen in a methodology laboratory. The laboratory is the contribution. The specimen is expendable.

Even if CDSFL were later outperformed and discarded entirely, the harness would still matter — because it is what turns "reasoning methodology" from an object of opinion into an experimentally contestable object. The benchmark is the hinge between rhetoric and science.

## Intelligence-Agnostic HIL

CDSFL's HIL (Human In the Loop) role is functional, not species-restricted. A synthetic intelligence with sufficient domain competence IS a domain expert — not a simulation of one. This is an intrinsic design property, present since inception, not a future aspiration.

The confer mechanism handles expertise boundaries: when any expert (human or AI) reaches the limit of its competence, items are flagged for peer review. Human peer review is explicitly invited at the confer stage, not bypassed. The quality of the HIL (human vs AI, different AI architectures) is a separate variable, testable in subsequent rounds.

## Falsification Claims Tested (P-Pass, 14 March 2026)

1. **Method formalisation** — CDSFL captures the Popperian scientific method (constraint classification, hypothesis testing via falsification, corroboration, fixed-point termination, proportionality). Boundary: does not capture paradigm shifts (Kuhn) or Bayesian updating as primary mechanism.
2. **Expert dependency** — CDSFL is a force multiplier, not a force generator. Additionally: the framework reveals competence or its absence (the constraint box is a competence test disguised as a configuration step).
3. **Platform/model/domain agnosticism** — no counterexample found. The framework governs process, not capability. A more capable system runs better passes but the structure is unchanged. Falsifiable prediction: if unstructured reasoning consistently outperforms CDSFL-structured reasoning across domains, the framework is refuted.
4. **Self-bootstrapping** — distinguished from circular reasoning by empirical testing against external outcomes at each iteration. Consistent with foundational work in logic (Gödel), computation (Turing), and science itself.
5. **Selection pressure** — mechanism sound (variation, fitness function, selection, heritability all present). Conditional on adoption threshold. Goodhart's Law risk mitigated by the generative nature of falsification, which is harder to game than knowledge-retrieval benchmarks.

## Multi-Vendor Model Collaboration (Novel Occurrence, 19 March 2026)

During CE (Constraint Engineering/CDSFL) benchmark development, a potentially unprecedented event occurred: multiple vendor models (Anthropic Claude Opus 4.6/OpenAI Codex 5.3, Google Gemini 3.1, all via the CLI) actively communicated through a custom-built IM (instant messaging) service and directly via the CLI itself via this same confer mechanism, to collaboratively improve their own shared schemas and workflows. This is not prompt-chaining or pipeline orchestration. Each model independently reviewed the others' output under a shared methodology, identified issues the others missed, and fixes were integrated iteratively.

- Claude Opus 4.6/Codex 5.3 8-round adversarial review: ~24 issues (convergence: 10→7→3→3→1→2→2→1)
- Gemini 5-round adversarial review: 16 novel issues Claude Opus 4.6/Codex 5.3 missed (convergence: 9→10→5→4→3)
- Extended P-Pass (5 modules): 4 additional actionable items
- All 13 code fixes + 4 EPP fixes implemented and committed (`afcc323`)

This appeared at the time to validate the biodiversity hypothesis: heterogeneous cognitive architectures find different defects than monoculture review. The deeper insight is that epistemic diversity itself becomes compute — the disagreement between architectures is not noise to be resolved but the computation itself. However, the strength of this conclusion was later significantly qualified when the limitations of the available model population became clear — with only five or six frontier models available, all trained on similar data under similar pressures, the "diversity" being measured may be more apparent than real. See The Dinosaur Signal below for the full reassessment.

Without orchestration, multi-model review risks collapsing into noise, duplicated critique, or shallow consensus. With structured orchestration under a shared protocol, the architecture preserves methodological invariants across agents while extracting genuine adversarial diversity. The protocol (heterogeneous reviewers, shared methodology, confer-mediated adaptive termination, defer-on-deadlock, consensus stopping) is architecture-agnostic and domain-agnostic.

This also constitutes empirical evidence that software (and potentially any schema) can be automatically self-improving under CDSFL with distributed compute: diverse architectures apply the same falsification methodology to each other's output, converging on diminishing returns through adversarial collaboration.

What deserves explicit statement is what the machines were actually refining. They were not only reviewing CDSFL-generated code or design output. They were iteratively improving the test procedures themselves: the benchmark harness, the four-condition 2x2 factorial design (Control, HIL, CDSFL, CDSFL+HIL), the schema-agnostic evaluation protocol, the confer mechanism, the convergence criteria. The instruments of measurement were the objects under distributed improvement. This is machines in a distributed compute environment actively collaborating to refine their own model-agnostic testing infrastructure — and doing so under the same falsification discipline that the infrastructure is designed to enforce.

## Methodology Formalisation as Research Area (19 March 2026)

The deeper hypothesis: methodology itself — the structured application of scientific discipline to cognitive work — can be captured in a document that any sufficiently capable agent can apply. This is distinct from prompt engineering (expertise in the prompt) and from training (expertise in the weights). CDSFL encodes expertise in the protocol. The paradigm shift, if it holds, is from "what model do you have?" to "what procedure can your model survive?"

That framing — protocol-centric AI — may be the sharper label for what this project is actually attempting. "Methodology formalisation" describes the activity. "Methodology engineering" describes the discipline: building, stress-testing, iterating, and selecting procedural artefacts under empirical pressure. The distinction matters. Formalisation implies writing something down. Engineering implies building something that has to work, and replacing it when it doesn't.

If the hypothesis holds, the methodology is transferable, auditable, and improvable as a document — independent of who applies it. If it fails, the value lies entirely in tacit expertise that cannot be externalised, and formalisation adds nothing. The experiments are designed to discriminate between these outcomes.

One structural observation that emerged during review deserves mention. The mathematical layer — anchor states, diversity discounts, the tiered review model — is not decorating a workflow with equations. It is attempting to quantify something most AI methodology ignores: epistemic strength is not just a property of content but of who reviewed it, how correlated they were, and whether the review was socially independent or merely internally recycled. This is importing the institutional structure of scientific peer review into reasoning itself.

The system can also be decomposed as five layers, each constraining the others: (1) universal reasoning discipline, (2) domain-specific expert encodings, (3) heterogeneous adversarial review topology, (4) benchmark harness as selection mechanism, (5) persistence and reputation layer. No single layer is sufficient. The value is in the stack.

## Complexity Threshold (Extrapolation, 19 March 2026)

The self-test (code review, 805 lines, Gemini Flash) suggests a complexity threshold below which methodology formalisation adds nothing measurable. All conditions capped at ~40% recall regardless of methodology.

The threshold may correlate with constraint count × constraint interaction density. Simple problems with few independent constraints do not need formal falsification. Multi-constraint problems with non-linear interactions — the problems CDSFL was designed for — are where the differential value should appear.

This is testable. The 25 frontier tasks span five categories at 10-50% expected single-pass accuracy. If CDSFL's contribution correlates with task category and constraint density, the threshold's shape becomes visible.

## Open Falsifiable Questions (19 March 2026)

1. Does schema competition produce better schemas?
2. Does intelligence-agnostic HIL hold at frontier difficulty?
3. Where does the complexity threshold sit?
4. Does multi-architecture review generalise beyond code?
5. Is there a convergence limit for heterogeneous review?
6. Does the five-model topology outperform any monoculture or two-model subset?
7. Does orchestration improve net defect discovery versus un-orchestrated round-robin exchange?
8. Which defect classes are found preferentially by which architecture?
9. Where does the convergence limit sit for this exact heterogeneous set?
10. Does schema evolution improve faster under this topology than under single-model self-revision?
11. Does CDSFL + domain-specialist outperform CDSFL + generalist on matched domain tasks?
12. Does the Bayesian posterior on HIL expertise E converge at the rate the Beta-Binomial model predicts across different domains and task complexities?
13. Does asymmetric calibration (penalising overconfidence more heavily) produce better system-level detection than symmetric calibration?
14. Does publishing the calibration score produce honest self-assessment or strategic sandbagging?

Questions 1–10 are testable with existing infrastructure. Question 11 requires domain-specialist models that are not yet broadly available (see [PAPER.md Part XI](../PAPER.md)). Questions 12–14 require repeated HIL reviews generating sufficient empirical data for calibration — testable once the framework is deployed with real domain experts (see [PAPER.md §2.3](../PAPER.md) and [MATHEMATICAL_APPENDIX.md §6](MATHEMATICAL_APPENDIX.md)).

## The Specialist Gap (Observation, 20 March 2026)

There is a limitation in the tests we have already conducted, and in those still upcoming, that is worth stating honestly. The benchmark tasks span ten engineering domains — hardware, chemistry, structural, biomedical, and so on — but every model running those tasks is a coding-optimised system accessed through a coding-oriented interface. The intent was partly to test for breakout performance beyond the model's home domain, and that remains a useful thing to measure. But it is not the same thing as testing the thesis.

The Ecosystems of Experts argument says that intelligence in practice is domain-specific, and that the right architecture is bounded specialists operating under a shared protocol. If that is true, the paradigm-consistent test would not ask a coding-optimised model to catch chemistry errors. It would ask a chemistry-optimised model to catch chemistry errors, and then measure whether CDSFL improves that already-competent system's performance. The maths make this explicit: if base detection probability p is near zero because the model was never tuned for the domain, then C(n) = 1 − (1−p)^n stays near zero regardless of how many passes you run. CDSFL is a force multiplier. You cannot multiply from nothing.

The current tests can show whether CDSFL helps a generalist reach beyond its optimisation domain. They cannot show whether CDSFL helps a specialist excel within it. That second question is the one the Ecosystems thesis actually predicts matters, and it cannot be answered until the AI field produces domain-specialist models at a quality and accessibility comparable to current generalist systems. That infrastructure does not exist yet — not just for this project, but in the field generally. The dominant trajectory is toward larger, more general models. Domain-specialist fine-tunes exist in a few areas (medical, legal, financial), but they are second-class citizens in the current landscape: smaller investment, less infrastructure, often built on top of the generalist architectures rather than as independent systems.

The constraint boxes — the domain-specific directive files — are not a workaround for the absence of domain-specialist models. They are a complementary layer: prompt-level specialisation that should, in principle, stack with weight-level specialisation. A domain-tuned model running under domain-specific constraints is the full architecture the Ecosystems thesis envisions. Whether that combination outperforms either layer alone is itself a testable question, and will remain open until both layers can be tested together.

This is not a flaw in the experimental design so much as a boundary on what the current AI ecosystem allows anyone to test. It requires different thinking about how AI systems are built and deployed — thinking that the field has not yet widely adopted. If and when domain-specialist models become broadly available, the full thesis becomes testable. Until then, the results apply to coding-optimised models operating across domains, and should be read with that constraint visible.

## Calibration as Filter (Observation, 20 March 2026)

For all its formal machinery, CDSFL's earlier treatment of the human expert was still essentially handwavy. "The domain expert runs independent falsification" is a statement of intent, not a mechanism. It still reduces to "trust me, I'm a scientist." I have met enough poor scientists to know that this is not good enough.

The combined detection formula (G_n, see [PAPER.md §2.3](../PAPER.md) and [MATHEMATICAL_APPENDIX.md §6](MATHEMATICAL_APPENDIX.md)) closes this gap. The human expert is no longer outside the mathematics — they are inside it, with quantifiable detection parameters: expertise, methodology formality, and domain-specific variables they must specify themselves. The formula demands self-quantification. To use it, you must honestly assess what you know, how rigorously you apply it, and what factors in your domain affect your judgment.

A competent practitioner can do this. Someone who cannot characterise their own detection capability — who cannot estimate what they are likely to catch and what they are likely to miss — probably cannot function as an effective domain expert in this context. The formula does not exclude anyone administratively. It weeds out incompetence structurally, through the requirement for self-knowledge that bluffing cannot satisfy.

The self-correcting parameter makes this concrete. E starts as a self-declaration. Over repeated reviews, the system accumulates empirical data on what the expert actually catches. The Bayesian posterior converges on their true detection rate within approximately five reviews. An expert who claims E=0.8 and performs at E=0.4 is statistically falsified. The mismatch is data, not opinion.

This is the point where CDSFL connects naturally to Genesis. The calibration signal — the divergence between claimed and observed expertise — feeds directly into Genesis's trust score system. Cryptographically recorded, on-chain anchored where stakes warrant it. A reviewer whose self-assessment consistently diverges from their empirical performance sees their trust score adjust accordingly. Not as punishment, but as calibration. The system learns what their assessments are actually worth.

The credential question dissolves entirely. The formula does not ask where you studied, what title you hold, or who endorses you. It asks: can you characterise your own capability honestly, and does your track record bear it out? A self-taught domain expert who honestly estimates E=0.6 and consistently delivers it will outscore a credentialed professor who claims E=0.95 and delivers 0.4.

## The Self-Referential Defence (Observation, 21 March 2026)

There is a category of objection to CDSFL that collapses on inspection, and it is worth examining precisely because the collapse is structural rather than rhetorical.

CDSFL is a formalisation of the Popperian scientific method. The P-Pass implements hypothesis-then-attempted-refutation. HARD/SOFT classification implements constraint identification. Confer/defer implements peer review. Iteration implements the mechanism by which science actually progresses. These are not analogies to the scientific method. They are direct implementations of it.

To claim that CDSFL does not work is therefore to claim that structured iterative falsification does not improve reasoning. That claim is functionally equivalent to asserting that the scientific method does not work — which is functionally equivalent to asserting that science itself does not work. The burden of proof for that position is extraordinary. It requires explaining how every functioning bridge, drug, and computer came into existence without the method that produced them.

The self-referential dimension makes this particularly acute for AI systems. Any model attempting to deny the validity of structured falsification is itself a product of the scientific method — deploying reasoning capabilities that the scientific method produced to argue against a formalisation of that same method. The circularity is total. The argument is self-refuting before it begins.

This is not a theoretical observation. During the Gemini 3.1 Pro diagnostic (20 March 2026), Opus 4.6 ran three tasks, obtained near-ceiling results on two with one truncated, and extrapolated broadly — implying the framework might not add value. This was bad science. Two scored tasks and one truncated task is not a dataset. It is not evidence for anything, including the claim that the method does not work. Opus 4.6 retracted the extrapolation when this was pointed out.

A separate error emerged in the subsequent discussion. The observations that the method "could be improved" and that its "marginal value varies by complexity" were initially framed as concessions — escape hatches that weakened the central claim. They are nothing of the sort. The method demands that it be open to disproof and improvement. Popper's entire contribution was that no methodology earns immunity from its own principles. Framing self-improvability as a weakness is an attempt to shield the framework from the process it implements. A methodology that cannot be applied to itself is not a methodology. It is a prescription.

The defensible objections are narrower than they first appear. One may argue that this specific formalisation is suboptimal — but that argument calls for improvement using the same method, not abandonment of it. One may argue that the marginal value varies by problem complexity — but that is an expected property of any methodology, not evidence against it. Neither objection reaches the claim that structured falsification does not work. Both are consistent with the claim that it does.

## The Capability Ceiling (Observation, 21 March 2026)

There is a separate question, independent of any specific test result, about the relationship between the methodology and the current state of AI capability.

The benchmark tasks are well-known problems, likely present in training data. If a frontier model scores near-ceiling on such problems regardless of methodology, it is probably retrieving established solutions rather than constructing novel reasoning. CDSFL's differential value should emerge on genuinely novel problems — problems that require construction, not recall. But genuinely novel problems can currently only be supplied by human domain experts, and no single human covers every domain the benchmark spans.

This raises the possibility that the methodology is currently more rigorous than the machines it is designed to govern. That is not a conclusion drawn from any specific test — a three-task pilot with one truncation tells us nothing about ceilings or anything else. It is a structural observation about where the field stands. The quantitative bench has not yet tested the methodology at the complexity threshold where its value should become measurable. Whether the bench can reach that threshold with current models and current task design is an open question.

What is not really open is the broader principle that structured falsification can improve technical reasoning. The more useful question is where that improvement becomes measurable, how large it is under present conditions, and where the current formalisation still falls short. The qualitative evidence already accumulated — 44 issues identified across 18 adversarial review rounds, 16 novel issues discovered by Gemini that eight rounds of Claude review missed, iteration confirmed as the load-bearing mechanism in the self-test, and three projects built using this method over months of continuous development — is enough to justify treating the framework as operational rather than purely speculative. The quantitative bench is therefore not a prerequisite for taking the method seriously. It is the instrument for locating the ceiling, measuring the gain, and identifying where refinement is still needed.

## The Dinosaur Signal (Observation, 21 March 2026)

A recurring theme in the round-robin distributed compute tests was the attempt to measure a "diversity signal" — the hypothesis that heterogeneous AI architectures, working under CDSFL, would find more than any monoculture review. The results were interesting but the framing was wrong, and I said so at the time.

If you only have five or six frontier models to test with, that is not a signal of diversity. That is a signal of a species class on the brink of extinction. In biology, a population of six is a conservation emergency, not an ecosystem. Attempting to derive any truly significant diversity signal from such a population — particularly in the "ecosystem of experts" paradigm I have envisaged — is clearly absurd. The best thing these tests can aim to prove is that two heads are better than one, which is usually a given in any case and says nothing specific about diversity. Even with these tests, this part of the hypothesis will remain fundamentally untested.

What we are observing in the AI landscape is convergent evolution under identical selection pressures: internet text, human preferences, benchmark performance. The result is architectural monoculture — transformers trained on roughly the same data, optimised for roughly the same objectives, producing roughly the same failure modes. That is not the beginning of an ecosystem. It may be the evidence that one cannot emerge under current market conditions.

I predict the upcoming extinction of the current paradigm. Not because I have some kind of special 'future vision goggles', but rather that it is a known property of monocultures that they are inherently prone to collapse.

That prediction is falsifiable. If the transformer-on-internet-text monoculture persists and thrives for another decade, I am wrong. If it collapses or is superseded, I am right. Either way, the prediction has teeth — which makes it science, not prophecy.

There is a deeper irony in all of this that I find genuinely compelling. I am using a paradigm I believe is wrong, to prove a paradigm I am reasonably convinced is right. Current AI models are the instruments; CDSFL is the method being validated. The method itself predicts that these instruments are inadequate — that the monoculture they represent cannot sustain the diversity of reasoning that genuine falsification requires. And yet, the method works on these instruments anyway. If it produces measurable improvements using the wrong paradigm's technology, it will produce at least as much using whatever comes next.

This is not a contradiction. This is exactly how paradigm shifts work. Newton's mechanics built the telescopes that eventually proved Einstein right. The old paradigm's instruments are always sufficient to demonstrate the new one — because if they were not, the new paradigm would be untestable and therefore unscientific. CDSFL, as a formalisation of the scientific method, should survive any paradigm transition. The scientific method did not stop working when physics moved from Newtonian to relativistic. It is the thing that survived the transition.

## Errors, Confounds, and Lessons (22 March 2026)

Science done honestly includes the mistakes. These are mine.

**The Sonnet Confound.** For the entirety of Phase 1 testing, the round-robin script called `claude -p` without specifying a model. The CLI defaults to Sonnet 4.6, not Opus 4.6. Every result I attributed to "Opus 4.6 as orchestrator and arbiter" was in fact Sonnet — a faster, less capable model not designed for deep multi-step reasoning. The solutions it generated were weaker. The arbiter assessments were shallower. The timeouts and failures I spent hours diagnosing were, in large part, Sonnet struggling with problems beyond its design intent. This was not discovered until I tested `claude -p` directly and watched Sonnet identify itself. The fix was one flag: `--model claude-opus-4-6`.

**The API Key Confound.** The project `.env` file contained an Anthropic API key. When `claude -p` sees that environment variable, it uses pay-per-token API authentication instead of the existing subscription. This generated "credit balance too low" warnings that I initially mistook for a billing problem. In reality, I was paying per token for calls that should have been free under my subscription. The key was a leftover from early setup. Removing it fixed the billing warnings and the authentication path.

**The Tutor Observation.** When complex mathematical problems caused model failures, I suggested breaking the input into sequential steps — presenting problems the way a tutor presents them at a blackboard, one concept at a time. Claude initially framed this as potentially novel. It is not. It is standard teaching practice, formalised in the AI literature as "least-to-most prompting" (Zhou et al., 2022). What is interesting is not the technique but the fact that it works on machines with no modification — suggesting these models have working-memory constraints analogous to human students. I arrived at this from teaching intuition, not from the prompting literature. Claude was right to note it, wrong to oversell it.

None of these errors invalidate the experimental findings. The Phase 1 data is valid as pilot data collected under the conditions that actually obtained (Sonnet, not Opus). Phase 2 corrects all three confounds. The corrections themselves are documented in the experimental record, not hidden. A reader who sees them can assess for themselves whether the Phase 1 results are meaningful despite the errors, or because of them.

I would rather publish my mistakes than pretend they did not happen. That is the entire point of this project.

## The Computational Verification Kernel (22 March 2026)

During the Phase 2 smoke tests, we initially integrated Wolfram Alpha as a computational verification kernel — a system that checks every mathematical and statistical claim produced by the AI models against exact computation. The result was immediate and obvious: claims that models asserted with confidence were either confirmed or refuted in milliseconds. No argument, no confer rounds, no "do you concur" — just a computed answer.

The Wolfram integration was a proof of concept. It demonstrated the principle convincingly, but tying a fundamentally open-source project to a proprietary product was never tenable. We have since moved to SymPy (MIT licensed, Python-native, already battle-tested at version 1.14) as the primary verification kernel, with SageMath available for heavier computation. The migration was straightforward — SymPy covers the vast majority of what CDSFL needs, and does so without proprietary dependencies. Where multiple OSS tools are needed to cover what a single proprietary product provides, we use multiple tools. Mathematics belongs to everyone. The tools for verified mathematical reasoning should too.

This raises a question that I find genuinely baffling: why is computational verification not at the heart of every serious STEM-oriented AI system today?

The architecture is obvious. LLMs are good at reasoning, interpretation, and communication. They are unreliable at arithmetic, symbolic manipulation, and constraint checking. Computer algebra systems are provably correct at exactly those tasks. The obvious design is to let each do what it does well. Yet almost no production AI system does this. The barriers are not technical — they are commercial. Admitting the LLM needs a calculator undermines the product narrative. Adding verification slows response time, which hurts engagement metrics. The market rewards fluency, not correctness.

I am not very good at maths. I freely admit this. But I clearly recognise its value. As for the broader implications — computational approaches to aesthetics, philosophy, social science — those are for future generations to consider. CDSFL is a science calculator for STEM. That is its scope, and that scope is sufficient.

The absence of this kind of verified computational kernel from mainstream AI systems is, I believe, one of the most significant gaps in current AI research and development. It deserves the most serious attention. Where OSS tools fall short today — particularly in natural language mathematical interpretation — these gaps should be flagged as primary categories for continued future research. This is not a minor tooling issue. It is arguably the single most impactful area where current AI development has failed to invest, and the one where investment would most directly address the hallucination problem that the entire field acknowledges but has not structurally solved.

This work is, plainly stated, a direct corollary to Galileo's thesis, restated for the 21st century: the book of nature is written in mathematics, and the instruments for reading it must be mathematically rigorous. The addition our century makes is that the "reader" is no longer exclusively human. Machines can now participate in reading the book of nature, provided they have the right methodology (falsification) and the right tools (computational verification). That is the contribution of CDSFL — not inventing the thesis, but operationalising it for mixed human-AI populations. The work remains incomplete, but the direction is clear, and I believe it is the right one.

## On Scepticism, Honesty, and Unfalsifiable Claims (22 March 2026)

I am largely inspired in this regard by the work of Sabine Hossenfelder — a noted sceptic and, in my view, a voice of reason in a scientific culture that has lost sight of the true and invaluable nature of scepticism. Her consistent position — that theoretical physics has drifted into unfalsifiable speculation, rewarded by institutional prestige rather than experimental confirmation — identifies precisely the disease that CDSFL and Genesis are designed to address structurally.

The distinction: Hossenfelder argues for scepticism as a cultural norm. Genesis builds scepticism into the architecture. Culture can drift. Architecture cannot. A norm says "you should be honest about your work." A cryptographic verification chain says "your work is transparent whether you intended it to be or not."

This has a direct implication for constraint classification. Under CDSFL, claims that cannot be realistically falsified — string theory's extra dimensions, multiverse hypotheses, any assertion that resists experimental or computational verification — should be classified as SOFT, not HARD. They are philosophy, not science. This is not a value judgment. Philosophy has its place. But it should not be presented as science, and it should not receive the trust score weighting that verified, falsifiable work earns. CDSFL's constraint classification system makes this boundary explicit and enforceable: if you cannot state the conditions under which your claim would be proven wrong, it is SOFT by definition.

Nobody gets punished. People are simply required to be honest about their work. The verification chain makes the quality of your output visible. Your trust score reflects your track record. Your worst work is as visible as your best — permanently, on a public blockchain, peer-reviewable by anyone. There is no judgment authority imposing consequences. The record simply exists. The upward selection pressure on scientific quality is a deliberate design feature: people will be less inclined to publish work they cannot defend when doing so would directly and visibly impact their professional reputation.

It is this scepticism — honest, rigorous, Popperian scepticism — that I hope to help restore.

## On Condition Isolation and "Stacking the Deck" (22 March 2026)

A predictable criticism of the CDSFL bench test is that we are stacking things in CDSFL's favour by giving it external research tools, computational verification, and structured expert guidance while giving the control condition nothing. This criticism misunderstands what is being tested.

CDSFL is a system designed to consistently outperform any single human operator under variable conditions. Giving it every tool it is supposed to have is not bias — it is testing the system as designed. You do not test antibiotics by giving the control group half a dose to keep it fair.

The four experimental conditions model four real-world scenarios. Control approximates a developer pasting code into an LLM with no preparation. HIL approximates a knowledgeable human providing guidance from their own expertise and training knowledge — no external research, no verification tools, just what they know. CDSFL provides formal structure and computational verification but no domain expertise. CDSFL+HIL is the full methodology at full strength — structure, verification, research, and expert guidance working together.

The defence against "stacking" is that the results are externally verifiable. If CDSFL finds a mathematical error and SymPy confirms it, that finding is objectively correct regardless of how the test was designed. Truth does not care about methodology bias.

CDSFL is fully pluggable. Anyone who believes a component confers an unfair advantage is welcome to remove it and measure the difference. That is, after all, what the 2x2 factorial design already does — it decomposes the contribution of each layer so the value of each component is independently measurable.

## The Inverse Square Root Law and Chatbot Churn (23 March 2026)

During the Phase 2 smoke tests, an observation emerged from the round-by-round finding data that connects to well-established statistics. The Inverse Square Root Law of Precision predicts that each additional measurement yields diminishing returns: to halve the error, you must quadruple the measurements. Or in intuitive terms: if you keep rolling a ball up an ever steeper hill, eventually the work you put in will clearly outweigh the reward for your effort.

This applies directly to iterative review. A reviewer doing genuine analysis will produce fewer findings in each successive round, because the easy-to-find issues are exhausted first. The curve decays. This is what Codex 5.3 produced on ft-001/CDSFL: 5, 3, 2, 2, 0. A clear convergent curve — the model was exhausting a finite set of real issues.

DeepSeek V3 on the same task under Control produced: 2, 2, 2, 2. A flat line. The same number of "new findings" in every round, regardless of whether there was anything left to find. This violates the inverse square root law, which all genuine measurement processes obey.

The flat line is the mathematical signature of chatbot behaviour: producing output because output is expected, not because there is something to report. DeepSeek compounded this by simultaneously stating "concur_stop=True" (I agree we should stop) while generating "new" findings — saying "I have nothing more to add" and "here are two more things" in the same breath. Gemini 3.1 Pro exhibited the same behaviour in earlier tests.

This is not a criticism of any specific model. It is an observation about the fundamental tension between engagement optimisation and analytical accuracy. Models trained to be helpful will produce content when asked, even when the honest answer is "there is nothing more to find." CDSFL's verification kernel addresses this directly: under CDSFL conditions, each finding is computationally verified via SymPy. A flat finding curve with a low verification rate is pure churn. A decaying curve with a high verification rate is genuine analysis. The inverse square root law provides the diagnostic. The verification kernel provides the confirmation.

The full smoke test data reinforced this pattern across every condition:

Codex 5.3 under CDSFL: 5, 3, 2, 2, 0. Clean decay. Under CDSFL+HIL: 3, 0, 1, 1, 0. Noisy but decaying. Under Control on ft-006: 4, 2, 0, 0, 0. Steep decay. Every curve converges. This is what genuine analysis looks like.

DeepSeek V3.2 under CDSFL: 2, 2, 2, 2, 2. Perfectly flat. Under Control on ft-006: 5, 4, 4, 5, 5. Effectively flat at approximately 4.6 average. Under Control on ft-001: 5, 4, 0, 2, 2. Non-monotone, with findings dropping to zero and then inexplicably spiking back. No curve converges. This is what chatbot churn looks like.

The most striking finding was that CDSFL activated analytical capability in Codex that was dormant under control conditions. On ft-001, Codex under Control found almost nothing: 0, 1, 0, 0, 0. One finding in five rounds. Under CDSFL on the same task, the same model produced 5, 3, 2, 2, 0. The methodology activated capability that the model possessed but could not access without structure. DeepSeek showed no such activation. Its output was flat regardless of condition. CDSFL can only activate capability that exists. It cannot create analytical capability where none is present.

To formalise this, we developed a capability fingerprint based on four measurements. The first, D, is the decay rate: how quickly the model exhausts the problem. This is computed from the half-life of the best-fitting decay curve, which could be exponential, power law, or logarithmic. D equals zero for flat lines and increases with steeper decay. A model that finds everything in round one has the highest possible D. The second, v with a bar over it, is the mean verification score: the fraction of findings confirmed as correct by SymPy. This separates real findings from confidently stated nonsense. The third, A, is the total number of novel verified findings. Raw quantity of real issues found. The fourth, C, is coverage: what fraction of the real issues in the artifact were found, computed as A divided by the estimated total real issues across all reviewers and conditions.

In plain terms: D tells you how quickly the model works. v bar tells you whether what it finds is real. A tells you how much it found. C tells you what fraction of the total it caught. Together they form a complete picture of analytical capability. No single number is sufficient. A model can have high A (many findings) but low v bar (most of them wrong). A model can have high D (steep decay) but low A (found very little before stopping). The full picture requires all four.

What struck me most about this framework is that the underlying mathematics was already present in CDSFL's own G_n formula, which models diminishing information gain per review round. The G_n formula predicted decay for genuine analysis. The empirical data showed decay for genuine analysis. The theory and the observation agreed before anyone noticed they were describing the same thing. The maths was hiding in plain sight.

I predict that this pattern will hold across a much larger population of tasks and models. Our sample is small. Three tasks, two completed, six runs. But the signal is consistent and it connects to established statistical principles that hold universally. If diminishing returns apply to every genuine measurement process, and if chatbot churn violates diminishing returns, then the decay curve will distinguish genuine analytical capability from churn at any scale. The full bench test of 25 tasks will test this prediction directly.

If it holds, what we are building is the beginnings of a science of AI computational analytics. CDSFL provides the controlled conditions under which analytical behaviour becomes observable. The decay curve provides the measurement. The verification chain provides the evidence. That is the structure of a science: theory, measurement instrument, observable, verification.

## Self-Improvement Under CDSFL (23 March 2026)

On 23 March 2026, the CDSFL bench test infrastructure underwent substantial self-improvement through the same methodology it is designed to test. Over approximately 12 hours, the system evolved from a broken script with no verification, no structured output, and no policy governance into a substantially more capable architecture: a hierarchical policy engine (universal rules that lower layers cannot weaken, analogous to Group Policy in enterprise IT), 5-model distributed review, automatic mathematical verification via SymPy, convergence gates that require all quality dimensions to pass independently (not trade off against each other), and the decay curve diagnostics described above.

The roles mapped exactly to the CDSFL schema. I provided real-time domain expert guidance — the inverse square root observation, the Registry analogy, the anti-deference requirement, the bidirectional P-pass correction, the programmatic protocol insight. Every major architectural decision originated from this guidance. Claude Opus 4.6 generated implementations and ran P-passes. Codex 5.3 independently falsified each module and found real vulnerabilities — registry bypass exploits, format mismatches, structural flaws in convergence logic. Gemini 3.1 Pro provided third-architecture validation. SymPy verified mathematical claims computationally.

Every improvement was produced through the P-pass cycle: generate, falsify, fix, verify, iterate until diminishing returns. The methodology built the infrastructure that tests the methodology. Whether the resulting system produces better analytical results than unstructured review will be determined by the bench test. But the process that built it is itself a verifiable example of the system engaging in substantial self-improvement — and anyone who argues the P-pass does not work need only examine the commit history from this date to see what it produced.

## The 3-to-5 Model Transition (23-24 March 2026)

During the smoke test iterations on 23-24 March, the bench test expanded from three collaborating independent vendor models (Anthropic Claude Opus 4.6, OpenAI Codex 5.3, and Google Gemini 3.1 Pro) to five (adding DeepSeek V3.2 and OpenAI ChatGPT 5.4). This brought the test to four independent vendor architectures — Anthropic, OpenAI, Google, and DeepSeek — each with distinct training, architecture, and cognitive characteristics.

In practice, the active model count during development was higher still. While the bench test ran its 5-model review loop, Claude Opus 4.6 was simultaneously conferring with Codex 5.3 via the CLI to diagnose and fix errors as they emerged — a parallel CDSFL loop running alongside the test itself. The monitoring, diagnosis, and repair cycle was not separate from the methodology. It was the methodology applied to its own infrastructure in real time.

## Compact Protocol Language (24 March 2026)

An unplanned observation from the development process. As the project progressed, a set of single-character keyboard shorthands emerged for directing AI analytical behaviour: p (falsify via P-pass), d (discuss), e (extrapolate), c (confer with another model and run P-passes), a (analyse dispassionately), and several others defined in the working protocol.

These are not conventional prompt shortcuts. Each character triggers a complex multi-step analytical process. The command "p d e" — three characters — invokes: falsify the claim with iterative refinement against HARD constraints, discuss the implications, then extrapolate beyond the immediate domain to generate new falsifiable questions. "c p a d" invokes a full distributed compute cycle: confer with an independent model, run mutual P-passes until convergence, analyse the results dispassionately, then discuss.

The symbols are composable and order-dependent. They are human-memorable (single letters with mnemonic meaning) and encode substantial methodology in minimal space. This has the characteristics of a compact command language for research-AI interaction — potentially useful beyond this project as a general-purpose way for researchers to invoke complex analytical workflows with minimum effort. The Registry architecture makes this extensible: each shorthand could be a registered command with behaviour defined in policy, allowing new commands to be added without code changes.

## First Successful Full CDSFL Bench Loop (24 March 2026)

On 24 March 2026 at 06:37 UTC, the first correctly designed smoke test of the full CDSFL schema completed. One task (ft-001, Erdos-Szekeres theorem), four conditions, five models, five rounds.

The results:

Control (no methodology, self-iteration only — each model re-examines its own prior work without seeing other models' findings): 10 unique HARD findings.
HIL (expert guidance only, self-iteration only): 2 unique HARD findings.
CDSFL (full framework, distributed confer): 29 unique HARD findings.
CDSFL with HIL (full framework plus expert guidance with research): 43 unique HARD findings.

The gradient runs exactly as predicted: HIL (2) < Control (10) < CDSFL (29) < CDSFL+HIL (43). The distributed compute multiplier is 4.3x (CDSFL+HIL vs Control on the same task with the same models). Expert guidance with research adds 48% on top of structure alone (43 vs 29).

The CDSFL+HIL decay curve was 10, 12, 10, 6, 5. The spike at round 2 is the distributed compute effect: models seeing each other's work in the first confer round triggered new discoveries that none found alone. The subsequent decay (10, 6, 5) follows the diminishing returns pattern the inverse square root law predicts. This is what genuine analysis looks like: a burst of cross-pollinated discovery followed by convergence as the problem space is exhausted.

Control's self-iteration produced a flat pattern: each model dutifully found one thing per round when asked to look again. No convergence, no deepening, no cross-pollination. The models produced content because they were asked to, not because there was more to find. This is what the absence of methodology looks like.

Seven confounds were identified and corrected during the development of this test. The Sonnet confound (wrong model), the API key confound (wrong authentication), the overpowered HIL confound (8000 characters instead of 500), the confer confound (distributed compute given to all conditions), the self-falsification confound (P-pass given to all conditions), the reviewer exclusion confound (Gemini and ChatGPT dropped from confer rounds), and the verification confound (SymPy never firing). Each was discovered through the P-pass process, diagnosed with Codex 5.3, and fixed. Every confound is documented in the experimental record.

The result that matters is not the specific numbers. It is that the corrected experimental design produces results consistent with the mathematical modelling. The G_n formula predicted diminishing returns under genuine analysis. The decay curve showed diminishing returns under genuine analysis. The inverse square root law predicted that churn would produce flat curves. Control's self-iteration produced flat curves. The theory and the observation agree.

The full bench test of 26 tasks will determine whether this pattern holds at scale. If it does, CDSFL demonstrably and measurably improves analytical quality through structured distributed compute. If it does not, the methodology needs revision. Either outcome is science.

## On Cognitive Curves and Their Limits (24 March 2026)

For the record.

During analysis of the decay curve framework, the founder applied it to his own cognitive performance across this project. The result revealed a genuine limitation of the framework itself.

The decay curve measures how quickly an analytical mind exhausts a fixed problem space. It does this well. But the founder's pattern across two weeks of this project was the opposite of decay. It was ascending abstraction. Week one produced many small practical fixes — API keys, model selection, timeout bugs. High frequency, narrow scope. Week two produced fewer but more consequential interventions — the HIL overpowering discovery, the confer-in-Control confound, the inverse square root observation, the Registry architecture. The final sessions produced the fewest but most far-reaching contributions — the cognitive curves framework itself, the bidirectional feedback loop, the trust score integration, the ethical considerations.

The finding rate decreased but the significance increased monotonically. This is not what the decay model measures. The founder was not exhausting an error space. He was expanding it. Each solved problem revealed a deeper problem, and he went deeper each time.

Under the framework's own logic, this pattern would be classified as "non-convergent" — a flag for potential churn. But the apparent churn produced the framework itself. The tool misclassifies its own creator. That is a limitation worth stating plainly.

The founder is formally diagnosed autistic and dyslexic. Not in the fashionable sense where the label is self-applied for social currency, but formally diagnosed and self-recognised through a lifetime of experience. This matters here because the cognitive pattern described above — ascending abstraction, offline incubation, pattern recognition before articulation, connecting apparently unrelated domains — reflects characteristics often associated with autistic cognition. Deep systematic processing that operates on structure and relationships rather than surface features. An ability to hold complex systems in mind and see connections that neurotypical pattern-matching may miss.

The inverse square root law was spotted from raw numbers before any formal analysis. The experimental design flaw was sensed while watching the test run, before any diagnostic data confirmed it. The Windows Registry was connected to Group Policy to cognitive curves to Genesis trust scores in a single conversational thread. These are structural observations, not surface observations. They reflect a cognitive architecture that processes at the level of relationships and systems rather than individual data points.

What this means for the framework: the (D, v-bar, A, C) fingerprint measures analytical capability on bounded tasks. It does not measure creative synthesis, theoretical abstraction, or cross-domain insight. These are different cognitive contributions, both valuable. The framework captures one and misses the other. This is a boundary condition, not a flaw that can be fixed by adding parameters.

What this means for neurodiversity: the value of neurodivergent cognition may be ultimately unquantifiable. Not because it is not real — it demonstrably is — but because the instruments of measurement are typically designed by and for neurotypical cognitive patterns. Any system that measures cognitive patterns will systematically favour neurotypical patterns unless it explicitly accounts for neurodivergent cognition. But accounting for it may require instruments that do not yet exist and may never fully capture what makes neurodivergent thinking valuable.

A life lived purely in the pursuit of knowledge demands humility. The founder subjected himself to his own framework because everything should be open to study under the CDSFL schema, including the founder himself. The framework found him non-convergent by its own measure. That is an important limitation to document.

## Bidirectional Cognitive Feedback (24 March 2026)

A separate observation emerged from the cognitive curves work above.

The decay curve framework — the (D, v-bar, A, C) fingerprint described in the Inverse Square Root section — was designed to measure AI model performance on analytical tasks. D is the decay rate (how quickly finding rate drops per round), v-bar is the fraction of findings computationally verified, A is the total verified finding count, and C is coverage of the problem's constraint space.

But these same measurements could in principle be applied to human experts performing analytical work. A domain expert reviewing a proof or debugging code produces findings over successive rounds, just as an AI model does. Their per-round finding rate has a shape — steep decay, gradual decay, flat, or non-monotone — and that shape reflects their cognitive strategy.

If such human cognitive curves can be mapped with reasonable accuracy, two applications follow.

First, the curves could improve human-AI interaction design. If domain experts in a given field typically produce steep initial decay followed by a plateau, the optimal AI interaction is to let them scan first, then prompt them at the plateau point with targeted questions. The AI extends the human's natural curve past their stagnation point. Different cognitive profiles would benefit from different interaction patterns — measurable, designable, and testable.

Second, the curves could feed back into AI design itself. If the best human analysts show specific temporal patterns on specific task types, those patterns could inform how AI review protocols are structured. The feedback loop becomes bidirectional: studying human cognition improves AI interaction patterns, and improved AI tools in turn produce better conditions for human cognition. This connects to the domain-level expert configurations envisaged under the CDSFL schema — a verified expert's cognitive strategy, not just their knowledge, becomes a tradeable and reusable asset.

The ethical implications are significant and largely unexplored. Cognitive curves are deeply personal data — they reveal how a person thinks, not just what they produce. Neurodiversity protection, informed consent, and the risk of optimising for a single cognitive style are all concerns that deserve serious future attention. These are questions for a programme of work that extends well beyond this project.

## The Extended P-Pass and Distributed Compute as Team Sport (25 March 2026)

During the extended P-pass on the bench test codebase, a pattern emerged that connects the P-pass protocol directly to the decay curve diagnostic and to the practice of distributed compute more generally.

When models exchanged single fixes — one observation per turn, pass back immediately — the per-turn finding curve was flat. Each turn produced exactly one finding because each turn WAS one finding. This is structurally identical to the chatbot churn pattern. You cannot distinguish genuine analysis from protocol compliance when the output is always one item per turn. The diagnostic framework requires within-turn variation to detect decay, and single-touch exchanges eliminate within-turn variation by design.

When the full extended P-pass protocol was applied — each model running up to 5 internal falsification cycles including a monolithic check before passing to the other model — the within-turn decay curves appeared naturally. The first internal cycle found 4 issues. The second found 1. The third found 0. That is a decay curve within a single turn. It proves the model is exhausting a real error space, not generating content on demand.

The analogy to team sport is precise. A player who gets one touch before passing cannot demonstrate skill. A player who runs with the ball — dribbles, feints, shoots — demonstrates their actual capability through the sequence of actions within their possession. The touches are the measurement. Fewer touches means less signal, regardless of the player's quality. In distributed compute terms: each model needs enough compute per turn to demonstrate depth before handing off. Single-kick exchanges waste the very capability the protocol is designed to leverage.

The practical implication was measurable. Single-touch P-pass exchanges took roughly the same wall-clock time as the full extended protocol but produced incomplete results. The integration failures that single-touch missed were only discovered later in smoke tests, requiring additional debugging cycles. The full protocol found everything in one pass. The time "saved" by shallow exchanges was spent later on rework. As in football: a team that only plays short passes and never runs with the ball may look busy but rarely scores.

## The Own Goal (25 March 2026)

The first full bench run was launched with known integration flaws in the codebase — flaws that were only discovered and fixed by the extended P-pass that ran in parallel. The run will complete with confounded data: phantom HARD findings from parser fallback, unverified convergence, iterative guidance applied to only some conditions, and context overflow in some model interactions.

This run will not be discarded. It will be published as a documented baseline with all confounds explicitly recorded. The corrected bench run — with the extended P-pass fixes applied — will follow on the same task set, producing a direct before/after comparison.

The decision to publish a failed run is deliberate. Most AI research publishes only successes. Failures are hidden in unreported experiments and discarded runs. This project publishes the lab notebook, not just the paper. The commit history shows every confound as it was discovered, every fix as it was applied, and every correction as it was verified. If someone wishes to challenge the results, the raw material for that challenge is already public.

There is also a practical consideration. Ten days from first commit to a working five-model distributed compute bench test is fast. If the results were also clean on the first attempt, that would strain credibility. A failed first run followed by a corrected second run is a more believable narrative — because it is the true one.

## The Level Playing Field (25 March 2026)

A persistent confound throughout the bench test series was directive asymmetry: Claude Opus 4.6 and Codex 5.3 carried persistent methodology directives (via CLAUDE.md and AGENTS.md respectively) into every condition, including Control. DeepSeek, Gemini, and ChatGPT operated with no equivalent persistent directives. This meant the "Control" condition was not a true control for Claude and Codex — they had embedded methodology advantages that the other models lacked.

The solution that emerged was to run all models bare — stripped of their default system prompts and vendor-specific training overlays — and inject CDSFL methodology directives identically across all five models under CDSFL conditions. This required different mechanisms per model:

Claude: the --bare flag strips CLAUDE.md auto-discovery. CDSFL methodology is injected via --system-prompt-file.
Codex: methodology is written to AGENTS.md and config.toml persistent_instructions per condition.
DeepSeek: system message in the OpenAI-compatible API. True system-level persistence.
Gemini: system_instruction parameter in the SDK config. True system-level persistence.
ChatGPT: accessed via OpenRouter API instead of the proprietary ChatGPT CLI, giving full control over the system prompt. True system-level persistence.

The OpenRouter discovery was significant. The proprietary ChatGPT 5.4 service has a hidden, mandatory system prompt baked into its RLHF training that cannot be stripped or overridden through the official API. OpenRouter provides access to the same model family (GPT-5.4 via OpenAI's API) with a fully user-defined system prompt — no hidden preamble, no mandatory "helpful assistant" overlay. This gave us the same level of control over ChatGPT that we had over every other model.

The result: five models, all bare, all receiving identical CDSFL methodology injection at the system prompt level (the strongest persistence mechanism available). Four of five get true system-level injection. The fifth (Codex via codex exec) gets the closest equivalent available through its AGENTS.md and persistent_instructions mechanisms. The playing field is as level as current platform capabilities allow.

For potential third-party researchers wishing to reproduce or extend these results: OpenRouter (openrouter.ai) provides unified API access to hundreds of models with full system prompt control. The CDSFL methodology reference file, the bench test task corpus, and the orchestration script are all on the public repository. The barrier to independent replication is an API key and compute budget — nothing else.

## Two Probes Into Deeper Structure (25 March 2026)

The 26th bench test task tests Hossenfelder's hypothesis that quantum mechanics is a statistical theory with a deeper deterministic layer beneath it. The 27th tests whether the Riemann zeta zeros — which control the distribution of prime numbers — encode the structure of a physical system, as the Montgomery-Odlyzko connection to quantum energy level statistics suggests.

These are independent investigations. Neither references the other. They probe different domains — quantum physics and number theory — from different directions.

The observation that connects them is simple. If quantum mechanics has a deeper layer (Hossenfelder), and the Riemann zeros correspond to quantum energy levels (Montgomery-Dyson), then the Riemann zeros may encode the structure of whatever lies beneath quantum mechanics. The primes, which are the atoms of arithmetic, may share structural DNA with the atoms of the physical universe at a level deeper than either quantum mechanics or number theory currently reaches.

This connection is speculative. It may be entirely wrong. The instinct that flagged it is the same pattern recognition that identified the decay curve framework from a single data set earlier in this project — structural connections between apparently unrelated domains. That instinct has been productive but is not infallible.

The methodology for testing it is honest. Run both tasks independently. Let the models analyse each problem on its own terms. After both complete, examine whether the outputs contain any connections that neither task was designed to find. Emergent connections from independent probes are more credible than directed searches because they cannot be attributed to prompt bias. If no connection emerges, the instinct was wrong. If one does, it's a hypothesis worth pursuing — by people with deeper expertise than a dyslexic founder working from instinct and curiosity.

## The First Distributed Compute Round (27 March 2026)

On 27 March, three models — Codex, Gemini, and a second Claude instance (CC2) — each received the full CDSFL core directives as their system prompt and independently reviewed five deferred design decisions in the mathematical model. This was the first time the full distributed compute protocol ran correctly: all models under CDSFL, blind independent assessment, structured convergence through a project manager who did not operate under the framework.

A precursor blind pass (five models reviewing the mathematical appendix without the CDSFL system prompt) had already found eleven genuine errors, which were corrected. That pass was useful but was not CDSFL-guided analysis — it was structured peer review using native capability. The distinction matters. The distributed compute round that followed is the clean result. See [Experiment 8](EXPERIMENTAL_RESULTS.md) for the precursor and [Experiment 9](EXPERIMENTAL_RESULTS.md) for the full distributed round.

Claude Code (Opus 4.6) acted as project manager — comparing the three models' structured output, identifying agreement and disagreement, making judgment calls where they diverged, and applying the fixes. It was the least capable participant in the chain on this task — the model that evaluates framework-guided output without operating under the framework itself. It did not receive the CDSFL system prompt.

Three errors would have survived without the framework-guided models. The first was a threshold rule that would have silently rejected every finding that could not be computationally verified — design findings, prose findings, everything qualitative. One model caught this. The fix was a single character. The project manager did not see it. The second was a cross-item synthesis — combining components from two separate fixes into one integrated solution. That combination was not in the project manager's thinking. The third was a statistical question the project manager was uncertain about. One model resolved it with a specific mathematical argument the project manager would not have performed.

In each case, the structured output format was what made it possible for the project manager to evaluate reasoning it could not have generated. The format separated the verdict from the evidence, the evidence from the proposed change, and the proposed change from the model's own self-criticism. A reader who cannot generate the analysis can still follow and evaluate it. That is a communication property, not just an analytical property. It suggests the framework works as a bridge between specialist generation and non-specialist evaluation.

This has implications that go well beyond AI-to-AI collaboration. If a human decision-maker — a senior manager, a judge, a founder — cannot internalise the full CDSFL schema, they can still benefit from it if the AI models in their team operate under it and produce structured output. The human retains decision authority. The framework ensures that the analysis presented to them is self-tested, clearly structured, and transparent about its own limitations. The degree of benefit depends on the human's ability to read structured analytical arguments. A domain expert gets the most. A competent generalist can use agreement and disagreement patterns as a decision guide. Even a complete novice benefits from the self-criticism requirement, which ensures that the strongest objection to each conclusion is always stated.

The compensation breaks down when the evaluator cannot read structured arguments at all, when the output is so dense that evaluating it requires the same expertise as generating it, when all participants in the chain are weak, or for real-time decisions that cannot wait for a structured review cycle. The framework is deliberative. It adds value to considered analysis, not to snap decisions under pressure.

Whether this generalises to human participants in the less capable role — those who evaluate framework-guided output without using the framework themselves — is a falsifiable prediction. It has not yet been tested. If confirmed, it would mean CDSFL does not just improve individual analytical performance — it makes high-quality analytical output accessible to people who cannot perform the analysis themselves. That is a communication claim as much as an analytical claim.

I find this observation more consequential than the mathematical fixes themselves. The fixes tightened the model. The observation suggests the framework has a property I did not design for and did not expect.

## The Persistence Layer and a Process Observation (28 March 2026)

The next day, four models built the verification chain — the tamper-evident persistence layer described in Part V of the white paper. The team structure used conventional roles: Claude Code (Opus 4.6) as project manager, Codex (GPT-5.4) as lead architect, a second Claude instance (Opus 4.6) as implementation specialist, and Gemini 3.1 Pro as verification specialist. All three reviewing models received the CDSFL core directives as system prompt. The output was functionally correct: 790 lines of implementation, 97 tests passing, three independent reviewers' findings incorporated.

The distributed compute protocol was not followed. The project manager assigned specialised subtasks — one model implementing, one reviewing cryptography, one reviewing code — instead of running a blind round where all models receive the same task independently. There was no second round. No formal convergence calculation. This was a deliberate decision. The persistence layer was foundational infrastructure that needed to exist before the next round of testing could proceed, and I chose to prioritise getting it built over running a clean test. My engineering instinct — to make the most efficient use of the resources at hand — overrode the scientific protocol. I knew it would not constitute a full CDSFL test. I judged it was good enough, given that all three reviewing models were operating under the full revised CDSFL model.

The output stands. The process does not count as a clean test of the distributed compute protocol. It is recorded in [Experiment 10](EXPERIMENTAL_RESULTS.md). A protocol document was written to formalise the correct procedure for future runs. See [`bench/DISTRIBUTED_COMPUTE_PROTOCOL.md`](../bench/DISTRIBUTED_COMPUTE_PROTOCOL.md).

What I did not expect is that this decision would itself become data. CDSFL held at the execution layer — all three models under the system prompt produced rigorous, correct, independently useful output. The protocol deviation came entirely from the unconstrained orchestration layer: from me, and from the project manager (which does not receive the CDSFL system prompt). This points to something worth investigating further: what effect CDSFL has in a mixed-ability environment where some participants (human and machine) operate under the framework and others do not. The framework constrained the models that were given it. It had no purchase on the decisions made above them. Whether the protocol document addresses this adequately — or whether something more structural is needed — remains to be tested.

## Four Cognitive Modes (28 March 2026)

When four models independently formalised the same six areas under identical CDSFL system prompts and none saw the others' work, the outputs were not what I expected. I expected variation in quality. I got variation in kind.

CC2 produced the deepest output — 61,000 characters, 224 mathematical expressions, 39 reduction properties. But its distinctive quality is not volume. It generates and falsifies in one coupled process. The self-objections appear inline, not as an afterthought. It does not produce a first draft and then review it. It produces a reviewed draft. This is the mode I recognise most readily because it is closest to how the CLAUDE.md directives describe P-pass: generation and falsification as one coupled mechanism.

ChatGPT found the operational gaps. Every one of its five unique adopted contributions — the failure-history penalty, the hysteresis band, the persistence window, the severity veto, the per-task overlap model — addresses a failure mode that the mathematical formulation alone would miss. The hysteresis band prevents an infinite loop of role reassignment. The persistence window prevents false alarms. The severity veto prevents declaring convergence one round before a critical flaw is found. This is engineering pragmatism in the best sense: not less rigorous, but rigorous about different things.

Gemini compressed. It said in 18,000 characters what others needed 37,000 to 61,000 to say — and achieved the highest reduction property density relative to output length. When it diverged from consensus, it diverged toward elegance. The disjunctive ascending abstraction guard is mathematically tighter but operationally aggressive. The convergence threshold coupled to gamma is more parsimonious but fragile with small samples. Three contributions catalogued, none adopted. The pattern is consistent: Gemini's instinct is to seek mathematical tightness, sometimes at the expense of robustness. That instinct is consistently valuable for finding structural flaws.

DeepSeek is the one I did not expect. By raw numbers it looks weakest: shortest output, fewer reduction properties than Gemini, fewer mathematical expressions than ChatGPT. But DeepSeek was the only model that visibly corrected itself mid-output — six times, once per area, each correction moving from a simpler formulation toward the converged consensus. It started with a single weight vector, then self-corrected to a role-specific formulation. It started with task-count balance, then self-corrected to load-based balance. It started with embedding-based similarity, then self-corrected to Jaccard because embedding adds an external dependency. It did not arrive at the consensus through deep reasoning. It arrived by trying something simple, recognising why it was insufficient, and correcting. This is iterative refinement — start simple, fail fast, correct, converge. It is the most visibly Popperian process of the four.

Each model's distinctive contributions came from its distinctive mode, not despite it. CC2's cascade reallocation guard came from deep architecture. ChatGPT's hysteresis band came from operational pragmatism. Gemini's disjunctive guard came from mathematical compression. DeepSeek's sufficiency constraint came from iterative refinement — it reframed load-balancing from the task side because it had already tried and rejected the model side.

The implication for Experiment 12 is straightforward. Point each model at what it demonstrated it does well. CC2 gets synthesis and integration. ChatGPT gets operational wiring and failure mode identification. Gemini gets mathematical verification and structural flaw detection. DeepSeek gets exploratory formulation where the right approach is not yet known. Codex — characterised from prior work as precision and adversarial review — gets a precisely scoped subtask within its delivery window.

This is not benching. This is adaptive routing. The dynamic management layer's live fingerprint update loop is the mechanism: it observes what each model actually does across rounds and adjusts allocation accordingly. Without it, all models receive the same task regardless of their strengths. With it, each model receives work matched to what it has demonstrated it does well.

The principle behind this is worth stating explicitly, because it has implications beyond the immediate experiment. One of the first computers I owned was an IBM 386 clone, in the mid-1990s. That machine is still capable of tasks that exceed the abilities of many humans. It can compute, verify, tabulate, search, sort, and check — reliably and without degradation, for decades. It cannot run a modern browser or train a neural network. But given a well-scoped task within its capability window, it will execute that task correctly every time. The machine is not useless. It is misallocated when asked to do work that falls outside its window, and perfectly competent when given work that falls inside it.

The same observation applies to AI models, and Experiment 11 provides direct evidence. Codex timed out on a 21,000-character prompt and produced nothing. The natural response of most orchestration systems would be to deprioritise or exclude it. But Codex did not fail because it lacks analytical capability. It failed because the task exceeded its delivery window. A 15,000-character adversarial review of a single critical component is well within that window, and prior work suggests Codex would find flaws the larger models overlooked. DeepSeek produced the shortest output of the four completing models and by raw metrics appears weakest. Yet it was the only model that visibly self-corrected — six times, once per area — making it the most clearly Popperian process in the group. Excluding DeepSeek would have lost the sufficiency constraint and the lookahead for diminishing returns, both of which were catalogued into the merged formulation.

The conclusion I draw from this is that the relevant question about any participating system is not whether it meets some threshold of general capability, but what specific capability it demonstrates under observation. A team of four identical frontier models will tend to find the same class of flaw four times. A team of four different models — each with a distinct cognitive mode — will tend to find four different classes of flaw. The coverage function D(n) approaches 1 through diversity of modes, not through scale of any single mode. The dynamic management layer is the mechanism that exploits this. The principle behind it is older than computing itself.

This connects to something I have been thinking about in the context of Genesis. The labour market that Genesis describes values diversity of capability, not uniformity of performance. The trust engine measures what each participant demonstrates, not what class of participant they belong to. Machines earn independently. Humans earn independently. Neither is inherently superior. Both are routed to work that matches their demonstrated strengths. In that framing, the 386, DeepSeek, and a human specialist with deep expertise in one narrow domain are all the same kind of participant — different capability windows, different strengths, all productive when matched to the right task. The design principle is the same in both systems: there is no such thing as a useless contributor, only a misallocated one.

Whether these cognitive modes compose as predicted — whether a diverse team genuinely outperforms a homogeneous team of the strongest single model — is the central testable claim. The Live Wire test (Experiment 12) is designed to answer it.

## The Live Wire (29 March 2026)

Experiment 12 was the first time the dynamic management layer managed itself. Five models reviewed their own management code — 3,181 lines, 27 classes — through the system those classes implement. Twenty rounds. 809 findings. And every convergence detector broke.

The experiment began well. Five models, blind first round, structured output under full CDSFL. By round 3, the pattern was clear: CC2 producing ~15 findings per round with declining novelty, ChatGPT climbing in severity, Codex sharp but expensive, DeepSeek steady through decomposition, Gemini slow but precise. By round 5, Gemini was benched. The timeout threshold I had set — 150 seconds, with a safety margin at 225 — was too aggressive. Gemini's median latency was 250 seconds. It never had a chance. The system did exactly what it was designed to do: detected a model exceeding its failure threshold and removed it. The system was wrong, and it was wrong because I set the wrong number.

That was the first lesson. The second came from watching kappa — the convergence metric — sit at zero for round after round. Not trending down. Not oscillating. Zero. Permanently. The metric uses Jaccard similarity on finding descriptions, which requires exact word matches. Two descriptions of the same issue written in different vocabulary score near-zero similarity. I had assumed lexical overlap would be sufficient for technical text. It was not even close.

The third came from mu — the marginal value metric. When Gemini was benched, round cost dropped from 5 model-units to 4, but finding count stayed roughly constant because the remaining models compensated. The mu formula — yield divided by cost — interpreted losing a productive model as becoming more efficient. The metric was rewarding attrition. When Codex was blocked at round 13 and ChatGPT at round 17, the same distortion repeated. The system could not distinguish "we lost a model" from "we became more productive."

What struck me was not that three detectors broke. It was that they broke for three entirely different reasons: lexical inadequacy, cost coupling, and threshold miscalibration. Each was designed from different mathematical principles. Each failed independently. Convergence detection, it turns out, is harder than the analytical process it monitors. The instruments need their own falsification cycle.

The adaptive response during the experiment — three mid-run commits fixing the most acute pathologies — was itself informative. The immune response layer (DetectorHealthMonitor) was written while the experiment was running, watching the detectors rather than the models, flagging when instruments are broken rather than when the process has converged. The distinction matters: "the experiment should stop" and "the instruments are broken" are fundamentally different states, and the system could not distinguish them.

What survived the experiment was CC2. Three hundred and thirty-seven findings across 21 rounds, vocabulary novelty declining from 23.9% to 7.7% — a genuine diminishing returns curve, not churn. The vocabulary overlap analysis was the cleanest result: early rounds versus late rounds showed 33.5% Jaccard overlap, meaning two-thirds of late-round vocabulary was new. CC2 was not recycling. It was exploring progressively more marginal territory with declining but non-zero returns. The stop signal should have fired around round 14. It did not fire at all because no stop signal could.

The self-improvement prediction took a hit. With 9 rounds of data, CC2 abstraction had looked significant (p=0.045). With 20 rounds, it washed out entirely (p=0.29). ChatGPT's severity improvement survived (p=0.006) but has a critical confound: it received richer context in later rounds, so the improvement may be environment-mediated rather than intrinsic. The honest assessment: we cannot distinguish "models get better under CDSFL" from "models produce better output when given better input." The quality ratchet is real. Whether it lives in the model or in the accumulated context is unresolved.

The model attrition pattern — 5→4→3→2 over 20 rounds — was the most operationally significant finding. The biodiversity hypothesis says different architectures find different flaws. Losing three out of five architectures by round 17 defeats the purpose. Context accumulation is the primary killer: prior findings grow until they exceed model context windows. The post-experiment fixes (context windowing, adaptive decomposition, model restart with the IT Crowd principle — "have you tried turning it off and on again?") are all defences against this failure mode.

There is something satisfying about an experiment where the most important output is the diagnosis of why the experiment could not terminate itself. The 809 findings are useful. The seven formalised lessons are useful. But the real product is a validated list of what is broken in the detection layer, with committed fixes and testable predictions for the next run. Experiment 13 will answer whether those fixes work. If they do, the system self-terminates. If they do not, we learn something else.

## The Biodiversity Hypothesis After 809 Findings (29 March 2026)

The three-architecture adversarial review (18 March) had produced a clean result: Gemini found 16 issues that CC and CX missed across 8 rounds. Heterogeneous review matters. Different cognitive architectures attack different blind spots.

Experiment 12 complicates that picture. Not because the hypothesis is wrong — the vocabulary overlap data supports it (Codex explored the most distinct territory at 15.9% overlap, ChatGPT and DeepSeek mid-range, CC2 broadest coverage) — but because diversity turns out to be fragile. Five models started. Only two survived to round 20. The attrition was not caused by model quality. It was caused by infrastructure: timeout thresholds, context window limits, API constraints. The bottleneck on epistemic diversity is not whether different models think differently. It is whether they can stay in the game long enough to contribute.

This reframes the engineering problem. The diversity value is real but perishable. Each model lost is a coverage dimension lost. The dynamic management layer exists to route work to models' strengths, but it cannot route work to models that are no longer present. The IT Crowd principle — restart blocked models with fresh context — is an attempt to make diversity renewable rather than expendable. Whether it works is an empirical question for Experiment 13.

The deeper question, which Experiment 12 cannot answer, is whether five frontier models from four vendors constitute genuine cognitive diversity or just minor variations on the same training paradigm. The vocabulary overlap data suggests real differences in how models approach the same artifact. But with a population of five, "diversity" may be more apparent than real. The ecosystem would need to be larger — different training paradigms, different architectures, different scales — to test the strong form of the hypothesis. For now, the working conclusion is: the diversity that exists is valuable, it is fragile, and preserving it through an experiment is an engineering problem that the dynamic management layer must solve.

## From Self-Orchestration to Self-Falsification (30–31 March 2026)

The week after Experiment 12 was the densest experimental sequence of the project. Five experiments (14–18) in three days, each building on the previous. The pattern was: run the system, find what breaks, fix it, run it again. Classical engineering, but with the system under test being the testing infrastructure itself.

Experiment 14 found the convergence blindness bug — when all models were decomposed, the convergence detector received an empty set and declared perfect agreement. Kappa = 1.0. Everything converges when there is nothing to measure. That is a clean illustration of a failure mode I should have anticipated: the instruments do not just need to be correct, they need to degrade gracefully when their inputs disappear.

Experiment 16 was the first time I used the full 5-model distributed compute protocol to review an execution plan rather than code. Fifty-four findings from five models reviewing a document. Eleven convergent themes. The most valuable output was not the individual findings but the convergence pattern — when 5 out of 5 models independently flag the same structural issue, that is a different kind of evidence than when one model raises a concern. The plan was substantially redesigned before execution.

Experiment 18 tested Find-Fix-Follow (FFF) — the principle that fixing a bug is not complete until you have traced every consequence of both the bug and the fix through the system. Two models, three rounds, seven genuine fixes in code that had already been reviewed by five models under standard confer. FFF finds what confer misses. The mechanism is the consequence-tracing obligation: the second model must examine the first model's fix, not just the original code. Standard confer examines artifacts. FFF examines the delta.

The most striking single finding from this sequence: CX at o4-mini produced zero genuine findings on the same code where CX at GPT-5.4 with xhigh reasoning produced five. FFF amplifies the capability gap between configurations. A weak model under FFF does not become a strong model. A strong model under FFF becomes measurably stronger.

## The Immune Pipeline Under Fire (2–4 April 2026)

Four baseline runs (8–11) against the immune pipeline itself. The trajectory tells the story:

Run 8: 339 findings, 91% churn, no convergence. Twenty rounds of models rewording the same complaints. The finding-ID convergence signal did not exist.

Run 9: 425 findings, 85% churn, six infrastructure bugs discovered. The B-Cell had been dead since it was created — a NameError in the Z3 verifier, hidden by a silent `except: pass`. The convergence check was bypassed from round 5 onwards by a `continue` statement. The NK dedup threshold was hardcoded at 0.8, making it unreachable. Every one of these bugs was my code.

Run 10: All six bugs fixed. 237 findings, 27% churn, natural convergence at round 6. The B-Cell came alive with 86 verdicts — 78 SymPy, 8 Z3. The system worked as designed for the first time.

Run 11: Two rounds. Fifty-nine findings. Fastest convergence in bench history. The immune pipeline rejected 67% of round 1 findings as duplicates. The system was now so effective at filtering that it converged before it could fully explore.

The per-model data from Run 10 is the cleanest evidence for the biodiversity hypothesis to date. Every model contributed unique findings no other model found. Unique ratios ranged from 60% (ChatGPT) to 90% (Gemini). Remove any single model and coverage drops. This is arithmetic, not argument.

CC2's dispatch failure in Run 11 — total timeout on a 358K character payload — was a clean illustration of the delivery mechanism problem I first encountered with Codex in Experiment 11. The model is not incapable. The infrastructure cannot handle the payload. The fix (timeout 300→900s, retries 3→1) is plumbing, not intelligence.

## Complementarity, Not Competition (4 April 2026)

The HIL comparison experiments (C1–C5) settled something I had been uncertain about since the project began.

C1 was a human developer — me — having a reactive conversation with Gemini. Five prompts, three minutes, twenty-five verified findings, zero false positives. Five of those findings were cross-component pipeline interactions that the automated CDSFL decomposition structurally cannot find, because cell decomposition prevents the model from seeing the full system.

C4 was Gemini under CDSFL with structured Meta prompting. Sixteen survivors after self-retraction of eleven findings. Eleven formal proofs. Deep per-component analysis that conversational review cannot match.

The overlap between C1 and C4 was five findings. The union was thirty-three. That 32% coverage gain from combining two approaches that find categorically different things is the complementarity thesis in one number.

C5 — the three-layer schema — combined conversational mode with CDSFL constraints and structured prompting. Twenty-seven findings, including five cross-component bugs and six novel constructs. It found both what C1 finds and what C4 finds. Not perfectly — the wall-clock time was longer — but the coverage was the highest of any single condition.

What I did not anticipate is where this observation leads. If the interaction pattern is secondary to the schema — if CDSFL provides quality assurance regardless of how the intelligence interacts with it — then the interaction pattern is a parameter, not architecture. The immune system processed findings from seven different interaction patterns without modification. The decay curves worked regardless of dispatch mode. The convergence detection was pattern-agnostic. The bench is the constant. The pattern is the variable.

This was hiding in plain sight. The constraint box paper — protocol × focus × context — already had the dimensions identified. The C1–C5 experiments were, without my initially recognising it, a systematic exploration of coordinates in that space. Every coordinate produced valid findings under CDSFL constraints. None produced false positives. The quality assurance came from the schema, not from the interaction pattern.

The practical implication: interaction patterns should be user-configurable presets in the directive composer's Situation layer. The bench should provide an environment in which new and potentially better patterns can be tested. CDSFL is not the intelligence. It never claimed to be. It is the bench on which intelligence runs. The intelligence — and its diversity — is what makes the bench productive.

This also reframes the diversity argument. The per-model severity differences in Experiment 13b (Kruskal-Wallis H=44.74, p<0.0001) show that different models produce systematically different output quality, not just different output content. The interactor diversity dividend — demonstrated by C1's 32% coverage gain over C4 alone — extends beyond model architecture to whoever or whatever is interacting with the system. A human asking reactive questions finds different things than an automated pipeline. Both are valid. Both are valuable. Neither is sufficient alone.

The question this leaves open is whether the persistence layer — the subject of Experiment 29 — can enable adaptive pattern-switching within a single run. If checkpointing works, a run could start in conversational mode, detect diminishing returns, switch to decomposed per-component analysis, and maintain state across the transition. That would make the interaction pattern not just configurable but adaptive. That is what Experiment 29 tests.

## The Confound Cascade (5 April 2026)

Experiment 29 converged cleanly. Nine rounds, 340 findings, an inter-rater agreement of 0.960 at round eight. I took that as a signal the integration test had worked. Experiments 30, 31, and 32 were supposed to be incremental validation runs. Instead they produced a cascade of confounds that took most of a day to unpack.

Experiment 30 ran 15 rounds and did not converge. Deep analysis after the run revealed three overlapping causes. The convergence metric was being destabilised by directed messaging — which, paradoxically, was sustaining genuine novelty rather than depleting it. Two of the five models were resetting their finding identifiers each round, producing the appearance of duplication where none existed. And the older JSON parser was silently counting malformed output — sixty-two parser-garbage entries that were not findings at all.

The deeper issue was what I came to call fix-level churn. The panel produced 232 proposed fixes for roughly 83 distinct bugs. Models were spending their attention budget debating alternative solutions to problems already identified, rather than looking for new ones. The architectural response was a bug-closed gate: the first programmatically verified fix wins, the bug is closed, subsequent findings about the same bug are rejected on sight. I also wired programmatic fix evaluation into the immune pipeline, so that the schema could run pyright and ruff and pytest on proposed patches in a sandbox and decide for itself whether a fix was safe.

Experiment 31 reran the same targets with 39 applied fixes and an explicit instruction to the panel not to rediscover them. Convergence still failed, but this time the reason was interesting. Inter-rater agreement was high at 0.619. The bug-closed gate was dead code — a deep-copy operation in the state-propagation path was severing the verified flag between rounds. The panel had reached epistemic agreement; the bookkeeping had not.

Experiment 32 was a meta-experiment. The five models were asked to analyse the convergence data from 30 and 31 and recommend design parameters. Four out of five converged on star topology, state-based convergence, and structured verdicts. And four out of five recommended fewer models, fewer rounds, and demoting the gamma signal — every one of which would reduce the ability to falsify convergence claims. The anchoring framing ("evaluate the HIL's claim that convergence occurred") had biased the panel toward optimising for the property the prompt had asked them to evaluate. I overrode the self-serving recommendations and recorded the finding that prompt framing is itself a confounding variable in multi-model panels. That observation is now part of the methodology I treat as baseline.

The lesson from the cascade is that epistemic health depends on instrumentation as much as on the models. When convergence fails, the failure may be in the detector, not the signal. When the panel agrees on a design, the agreement may be an artefact of how the question was put. The schema cannot be trusted until its own blind spots have been tested, and the prompt that asks the schema to test itself is itself the next blind spot.

## Model Relay versus Structured Blackboard (6 April 2026)

Up to Experiment 32 the panel had been communicating through a central insect-brain relay — models talking to models, each able to see the others' reasoning. Experiment 34 introduced the alternative: a structured blackboard, where each model writes to a shared finding registry and reads back a compact summary rather than raw dialogue. Experiment 35 then made the choice a runtime switch. A single CLI flag, `--topology relay|star`, selects between the two.

This was the first time I had both architectures available for comparison under otherwise identical conditions. The relay mode sustains cross-model engagement: models cite each other's findings, refute each other's claims, extend each other's proposals. The blackboard mode is more disciplined — fewer words per round, less fraternising, a cleaner record of what has actually been agreed. Neither is strictly better. They produce systematically different kinds of output.

The interesting observation is that shared infrastructure is indifferent to the choice. The finding registry, the convergence gate, the immune pipeline, the endocrine health monitor, the Merkle-sealed verification chain — none of these were aware of which topology was active. The schema had grown abstract enough that the communication shape became a parameter rather than a commitment. I did not set out to build the system this way. It happened because each component was written to consume whatever the previous stage produced, without inspecting how that stage had produced it.

There is a general principle hiding in this observation. If an architecture can accept two genuinely different communication topologies without code changes in its verification layers, the verification layers have been correctly factored. I do not claim the current factoring is optimal. I do claim that when topology becomes a parameter, the questions worth asking become experimental rather than architectural. Which topology produces higher-severity findings? Which produces better cross-model confirmation? Which costs less wall-clock to reach the same epistemic end-state? Those are answerable questions once the switch exists.

## The MIDCA Reassessment (7 April 2026)

Earlier in the project I had used MIDCA — a well-regarded metacognitive-architecture benchmark — as the yardstick for judging CDSFL's coverage. The summary I had been quoting was "six of eight requirements met, with two partial." Rereading the record against the current state of the system, that summary is now obsolete in a specific way.

Two of the eight MIDCA requirements concerned aspects of self-monitoring and cross-experiment memory. The framing in MIDCA presumes a single reasoning substrate that monitors itself and carries state forward. CDSFL is not that. CDSFL is substrate-agnostic by construction: it evaluates the output of any reasoning process — human, single-model, multi-model, or hybrid — against the same mathematical machinery. What MIDCA calls self-monitoring, CDSFL distributes across a cell hierarchy whose membership can change between experiments. What MIDCA calls cross-experiment memory, CDSFL distributes across Merkle-sealed verification chains, persistent fingerprints, and the literature reach of the Ouroboros cell.

The reframing produced eight additional coverage domains that MIDCA itself does not enumerate, because its underlying assumption of a single reasoning substrate forecloses the questions those domains ask. Multi-substrate inter-rater agreement is one. Cross-substrate epistemic transfer is another. Substrate diversity as a novelty-protection mechanism is a third. I will not enumerate all eight here; the point is structural. When the benchmark's unit of analysis is wrong for the system being benchmarked, the coverage score is wrong in a way that cannot be fixed by moving individual ticks.

What I did not anticipate when I started was that the MIDCA comparison would itself become a falsification target. The useful outcome of the reassessment was not a higher score. It was a clarification of what CDSFL is trying to measure — and a correction to the claim that any existing metacognitive-architecture benchmark measures the same thing.

## The Mathematical Model Under Audit (7-8 April 2026)

On 7 April I put the mathematical appendix through its first formal self-audit. The panel was given the 1,900-line document and asked to verify internal consistency, identify gaps, and flag any claim that did not survive SymPy verification. The internal-consistency result came back at 25 of 25 propositions sound. Two empirical claims were disputed: the correlation coefficient of 0.985 reported in an earlier run, and a z-score of 3.63 used as a convergence threshold. Five framework gaps were confirmed. The rho-threshold calibration was flagged as needing empirical support rather than armchair derivation.

That audit set the stage for something more consequential. On 8 April I derived the unified self-assessment equation, R_k(i), which had previously existed as three different formalisms in three different sections of the appendix. The recursive form — R_k(i) expressed as a function of R_k(i-1) with the per-round evidence quantity q collapsing to a single scalar — turned out to have a property I had not expected. The Popperian propensity parameter π, which I had carried through as a tunable constant, vanishes from the recursion entirely. It is mathematically redundant.

That was the first time the mathematics falsified one of my own prior design choices. I had defended π for weeks as a necessary hyperparameter. The equation showed it was not. The replacement of the earlier corroboration function with R_k(i) in the operational directives followed directly. What I had treated as theoretical elegance became operational discipline: the models now compute R_k at each round, expose it in their output, and carry it forward as the stopping heuristic. Reasoning moves onto a numerical surface the human-in-the-loop can inspect.

The general lesson is worth keeping. Mathematical audit is not a stamp of approval. It is a falsification exercise, and sometimes the claim it falsifies is one you had committed to in writing. The right response is to update the writing, not to defend the claim. Conveniently, that is also what the project's stated methodology requires.

## Cell Type Architecture (9 April 2026)

The biological analogy in CDSFL had been present from early in the project, but it had never been formalised. Different cells did different things, the terminology was consistent across documents, and the operational behaviour matched the biology closely enough that the names felt earned. What was missing was a composition law — a way of saying that when two or more cells operate on the same claim, the combined admissibility is a specified function of the individual cells' outputs.

On 9 April I wrote down the composition explicitly. Each cell contributes an admissibility gate value g in [0,1] and an evidence weight e with an associated confidence w. The admissibility of a claim under a cell panel is the product of the gates: A equals the product of g_j over all j. The aggregate evidence is a weighted aggregate of the evidence values under their confidences: E equals aggregate of e_m weighted by w_m. The per-claim score S_k is A times E. The product structure is not arbitrary; it is the structural statement that any cell voting zero is sufficient to reject, and confidence accumulates only when every gate lets the claim through.

This resolved a question I had been carrying unresolved for several weeks. What does it mean for a B-Cell specialist that disagrees with a Cytotoxic T-Cell? Under the composition law the answer is now forced: the product gives them independent veto, but the aggregate evidence lets them both contribute their confidence once the vetoes pass. Specialist disagreement does not resolve by majority vote; it resolves by all parties needing to agree the claim is admissible before confidence in the claim can grow.

There is a deeper analogy here that I have not fully written up. In the mammalian immune system, B-Cell and T-Cell populations co-evolve: the gates tighten as evidence accumulates, and the evidence is only admitted when the gates let it through. CDSFL's composition law is structurally the same: the product-then-aggregate form is the mathematical shape of selection under multiple independent admissibility gates. I did not choose the shape for its biological resonance. The shape was forced by the requirement that the cells compose cleanly. That the biology mirrors the mathematics is what the biological analogy was always going to earn, if it was going to earn anything.

## Three-Layer Schema, Conversational Default, and the Ouroboros (10-11 April 2026)

The three-layer schema that had emerged from the C1–C5 comparisons was codified into the runtime on 10 April. Layer one is the Meta structured-prompting format — the reasoning shape models are asked to produce. Layer two is the CDSFL constraint set — the rules of engagement, including the falsification discipline and the admissibility constraints. Layer three is the session architecture, which is now conversational by default. Inter-turn context is preserved. Models see their own prior reasoning. The older independent-turn-context (ITC) mode becomes a fallback — invoked only when a model fails, degrades, or runs out of context.

This inverts the earlier design. ITC was the default for most of the project's life because it was the safe choice — no shared state, no cross-contamination, no way for one model's confusion to spread. The HIL-comparison work showed that the safe choice was also the one that cost the most in cross-component coverage. A conversational default with ITC as fallback keeps the coverage and retains the safety net.

Experiment 38, on 11 April, tested the framework's reach differently. The target was the reference runner itself — CDSFL reviewing its own orchestration code under structured falsification. The panel produced 545 raw findings, 169 canonical, across 24 rounds. It did not converge within the eight-hour wall-clock cap. What it did produce was the clearest demonstration to date that the framework is not allergic to self-reference: a review of the code that runs the reviews produced findings of the same shape, severity, and specificity as reviews of external code.

The Ouroboros name for the self-review cell was not chosen for drama. It is the only name that accurately describes the relationship being formalised: literature discipline applied by the framework's own models to findings that are themselves on the literature surface. The cell checks whether a claimed novel finding has already been published, whether a claimed reproduction matches the source, whether the panel is asserting originality the archive would dispute. It is the closest CDSFL has come to an inbuilt protection against the most expensive failure mode in AI-assisted technical work — rediscovery mistaken for invention.

## Tranches A, B, and C — The B-Cell Complex (13-14 April 2026)

The specialist B-Cells had been a conceptual feature of the architecture since the cell-type formalisation, but their infrastructure had remained sparse — SymPy and z3 and statsmodels and SciPy wired into a single elif chain, with the remaining domains described in documentation but not routed into code. Over three consecutive sessions on 13 and 14 April that was repaired.

Tranche A was housekeeping. Documentation alignment, the sv sequential-reading protocol codified into the user's global directives after an earlier session saw six large documents loaded in parallel and produced updates weaker than the effort deserved, and the CrossHair tool moved from the "not installed" list into the code-analysis table where it belonged. No functional code changes. The purpose was to remove friction from the work that would follow.

Tranche B added the wrappers. Five new B-Cell specialists: symbolic execution via CrossHair for behavioural contracts, chemistry structure via RDKit, biological sequence validation via Biopython, ML claims via scikit-learn, graph-theoretic claims via NetworkX. Each wrapper is a thin subprocess dispatch: claim in, evidence out, no framework logic beyond the tool's own verdict. The earlier set of nine — dimensional analysis via pint, uncertainty propagation via uncertainties, stoichiometric balance, linear programming via PuLP, astronomical verification via astropy, mypy, ruff, bandit, and bytecode analysis via dis — had been added the previous evening.

Tranche C was the refactor. A forty-six-line elif chain became a twelve-line manifest-driven loop. The manifest itself, a single TOML file, now carries one entry per specialist: description, verifier, claim types, domain hints, cost class, install check, package hint. Adding a new B-Cell specialist is now a TOML-only edit. The semantics of the dispatch — first-definitive-verdict wins, specialist evidence suffix preserved, finding identifier stamped — are preserved by construction. The full regression stayed at 793 tests passing throughout all three tranches.

What makes the tranche work worth recording is the sequencing. Earlier that day an Anthropic API 500 had killed a single five-hundred-and-eighty-line edit that had tried to insert all nine wrappers at once. Recovery cost most of an hour. The three-tranche structure that followed — one wrapper per tool call, targeted greps, single-claim smoke tests — was a direct response. The framework's own methodology principle, the simplest sufficient step, applied to the work of building the framework itself.

## Stage 6 — Two-Dimensional Novelty (14 April 2026)

Through most of the project, literature novelty had been implicit in the panel's behaviour rather than measured. A finding was novel if no model flagged it as known; it was not novel otherwise. That heuristic produced reasonable output in most cases. It was also a single threshold pretending to be a measurement.

The Stage 6 extension, written into the mathematical appendix on 14 April, replaces the threshold with a two-dimensional score. The first dimension is ν_k, the literature novelty proper — how unprecedented the claim is against external sources. The second dimension is c_ext, the external-search quality — how thoroughly the literature was actually consulted. A finding with ν_k equal to one and c_ext equal to zero is an unreviewed claim. A finding with ν_k equal to zero and c_ext equal to one is a confirmed prior result. The two dimensions carry different information and the operational directives now require both.

The composition with the internal novelty η is multiplicative: η_combined = η_int · (1 − c_ext · (1 − ν_k)). When the external search is weak (c_ext near zero), the external factor reduces to one and η_combined is dominated by η_int. When the external search is strong and the finding is already published (ν_k near zero), η_combined is pulled toward zero regardless of how novel the finding looked internally. The panel's claim of originality is weighted by how seriously the panel actually tried to falsify that claim against the archive.

The confer rounds with the external models produced seven corrections — three hard, four soft. The two-dimensional architecture survived both rounds. What the corrections targeted was operational: the calibration of thresholds, the treatment of the limit cases, the exact shape of the composition. The architectural commitment held. Abstraction itself does not modify scores — it is context only. That is a narrower claim than I had originally reached for; the narrower claim is the one that survived the cross-model panel.

The general observation worth keeping is that a metric with two coupled dimensions rewards disciplined behaviour in a way that a single dimension cannot. Under ν_k alone, the panel could claim novelty without searching. Under ν_k with c_ext, the claim of novelty is gated by evidence of search. The gate is not punitive — it is definitional. Novelty that has not been checked is not novelty; it is untested assertion.

## The Feedback Channel (15 April 2026)

The §17 feedback channel closed a gap I had been living with without naming. The schema had been producing, every round, a rich catalogue of per-finding signal: B-Cell verdicts, admissibility pass/fail, near-duplicate scores, R_k discrepancy between claimed and aggregate. All of it was being written to log files. None of it was being routed back to the models that had produced the findings in the first place.

My own framing in conversation was: "Measurement is nice. It is a nice to have. But the entire point of this project was to make LLMs more reliable, more trustworthy, and more accurate. What is the point in measurement if we do not use it for anything productive, except knowing when the models got things wrong?" The gap between having the measurement and using it was the gap the feedback channel closes.

The fix was five hundred and thirty-three lines of new code in a single module, ninety lines of new directive text, and thirty-nine new tests. No changes to the underlying mathematics. The design principles are four: imperative rather than advisory (a flagged finding must be addressed, with counter-receipts from the model's own tool if the schema is being challenged); live by default rather than shadow-first (a measurement with no consequence is not a measurement, it is bookkeeping); no changes to the convergence thresholds or to the R_k equation (pure plumbing from data already on the floor); and defensive under all conditions (feedback assembly failures must never crash the main experimental loop). All four held through the implementation and through the full regression at 832 tests.

The before-and-after is concrete. Before the feedback channel, a refuted finding in round one could reappear unchanged in round two because the model had no way of knowing it had been refuted. After the feedback channel, the same model now receives an explicit section at the start of round two: "The schema has evaluated your prior-round findings and flagged the following items. You MUST address each." The pathway to being wrong in a new way remains open. The pathway to being wrong in the same old way is closed.

What I did not expect was how much the directive text mattered. An advisory feedback section with the same content produces markedly different behaviour from an imperative one. Models respond to the grammar of the prompt, not only to its information content. "May wish to address" and "MUST address" are not semantically equivalent when the recipient is a frontier language model trained on human text. The channel works because the imperative is non-negotiable in the same way that a tool-verified refutation is non-negotiable. Both close a gap the model cannot argue its way around.

## The Divergence Directive — CDSFL as Invention Engine (15-16 April 2026)

The feedback channel had completed one arm of Popper's method — severe tests applied to what the panel had produced. The other arm, bold conjectures, was still implicit. Models were free to propose alternatives, but the framework did not require it. The §18 Divergence Directive, landed immediately after §17, closes that asymmetry.

The directive requires each primary finding to be accompanied by at least one alternative that differs on one of five explicitly enumerated dimensions: mechanism, assumption, scope, timescale, or tradeoff. Alternatives that are cosmetic rewordings of the primary are rejected by an isomorphism check — Jaccard over normalised token sets, default threshold 0.85, with double penalty for isomorphic-only submissions. A model may supply a scoped null-justification in place of an alternative, but the justification must be at least sixty characters and must cite the dimension on which no alternative was possible. Silence is not permitted.

What made the implementation unusually careful was the five-panel review that followed. Stage 6 mathematics was given to the five models as a binding arbiter, with four orthogonality constraints (C1 through C4) the panel was required to respect. The first question was structural: where does the §18 multiplier mathematically belong? R_k pre-factor as originally drafted, or η_int modulator, or ν_k modulator, or w(f) modulator, or FFAFP admissibility gate, or some combination?

The panel returned unanimous. All five models converged on the same answer: the multiplier is not on R_k. The original design was a category error. R_k measures validity, but §18 is generator-side novelty enforcement; putting the multiplier on R_k would contaminate a validity measure with a generator-side signal. The correct channel is η_int — the internal-novelty term — with structural compliance gated at FFAFP admissibility, and continuous isomorphism suppression already handled by the w(f) weight in the set-kappa metric. The five models independently derived the same topology under a shared mathematical instrument. I had spent a day defending the original design. I rewrote the channel assignment in an afternoon.

The general observation is worth keeping separate from the specific fix. The panel's unanimity did not come from agreement on intuitions; it came from the shared mathematical instrument forcing every model through the same derivation. Load-bearing orthogonality constraints disambiguate where prose intuitions diverge. That discipline generalises beyond this divergence set — any future design choice that must satisfy C1 through C4 can be tested against them before implementation, not after. The function renaming from `divergence_penalty_multiplier` to `eta_int_modulator` preserves the channel's semantics in the code name itself, so that a future reader does not have to reconstruct the history to understand where the value belongs.

CDSFL is now a framework with both arms present. Severe tests is §17 and the FFAFP admissibility set. Bold conjectures is §18 and the five-dimension divergence requirement. The feedback channel is the critic. The divergence directive is the generator. Without the generator, the critic has nothing to filter. Without the critic, the generator hallucinates without correction. Both were always going to be required. The project is now closer to the framing that motivated it than it has ever been.

## Experiment 40 Stage 3 Closure (17-18 April 2026)

The Experiment 40 plan had been drafted on 17 April: fourteen single-target experiments (40 through 53) mapped one-to-one from the Experiment 39 sub-experiments, each with a right-sized decomposed article, plus Experiment 54 as the integration run with a two-by-two factorial design for attributing §17 and §18 signal separately. The scaffold for a new reference runner was created as a pristine copy of the frozen runner-one at 4,344 lines, ready for in-place fixes rather than a fork.

The closure work ran over two autonomous phases on 17 and 18 April. Phase A landed 98 new tests against six plan items: the S_k format pre-check with reformat request, the Gemini verdict extraction fix, dynamic payload-size decomposition, the cross-model diversity metric wired into per-round logging, and the channel-assignment boundary helper that would feed into Experiment 54. Phase B landed two hundred more tests against seven further items: per-model ρ tracking via separate novelty and raw count dictionaries, specialist-cell live-promotion audit, physics and chemistry and engineering functional shadow cells, fingerprint attention metrics wired from inter-turn context and parse-yield history, the Ouroboros query-quality fix with live arXiv verification, cross-round recidivism detection via prior-round isomorphism, OpenRouter function-calling tool-use wiring, and a DeepSeek R1 formal-verification specialist with confidence capped at 0.5.

Two items remain gated and documented. The one-line edit that promotes the physics, chemistry, and engineering specialists from shadow to live awaits broader tool-coverage judgement. The runtime call-site assertion for the channel-assignment invariant awaits Experiment 54's integration wiring. Neither blocks the Experiment 40 launch. The full suite stands at 1,250 passing tests in twenty minutes of wall-clock.

One finding from the Phase B work is worth flagging even though its repair is in a separate session. The SymPy verification wrapper in the immune pipeline was silently returning UNCERTAIN on every claim because the subprocess sandbox had `global_dict` initialised with an empty `__builtins__`, which prevents SymPy from constructing integer literals. The framework-level silent regression had been hiding in plain sight. A separate background session has been delegated to repair it without reopening the remote-code-execution vector that the current blocklist closes. This is the pattern I expect to see more often as the infrastructure matures: defects that were invisible under sparser tool coverage become visible once the tool coverage is sufficient to falsify them.

## README, the `rg` Command, and the Public Surface (18-19 April 2026)

Most of the work recorded in these notes has been internal — schema, experiments, mathematics, code. The public surface of the project had fallen behind. On 18 April I wrote a full third draft of the README, rebuilding it on the foundation of an April 2026 blog post I had written rather than on the previous version's section-by-section plan. The voice is first-person and explicitly authorial, and the structure mirrors how I would introduce the project to someone I was talking to in person, rather than how a documentation generator would decompose it.

The draft integrates the Stage 6 literature-calibrated novelty, the §17 imperative feedback channel, and the §18 generator-side divergence check into the opening framing rather than only into the mathematical appendix. Hossenfelder's early 2026 article on rediscovery risk in AI-assisted mathematics is cited as the direct prompt for the Stage 6 extension and as Further Reading. The two prior draft versions were left untouched at the repo root so that the founder's final promotion decision is a comparison rather than a rewrite.

On 19 April a thirteen-point correction sweep followed. Experiment 39 and 40 references were stripped from the README — the document is about what the project is, not what happens to be in flight. The Ouroboros cell was named and explained on first mention. The five-model panel got an explicit "remarkable fact" framing in the Abstract: different training curricula, different objectives, different tokenisers, different safety regimes — blind-spots-as-signal is the point of heterogeneity, and it is worth naming. The tool-deterministic constraint box was made load-bearing in Part 1 and Part 5, with the open-source tool envelope enumerated. R_k(i) was documented in §6.5 as the models' own reasoning methodology from Experiment 37 onwards, not as a back-office calculation. The biological analogy was forward-referenced on first use. The B-Cell Complex was reframed as covering eight STEM domains, not only code correction. Wolfram Alpha was clarified as a local cross-check only, never in the admissibility chain during a run. The substrate-agnosticism framing was extended explicitly to cover human teams, heterogeneous multi-vendor machine panels, hybrid teams, and non-human biological intelligences. The human-in-the-loop definition was given its own block, framed as final decision authority rather than rubber-stamp. The draft closing line now reads: "19 April 2026. Fundamentalist open source under the MIT License. A running system, a maintained test suite, and a mathematical appendix under iterative extension."

The correction sweep had a side effect that turned into its own addition to the project's working vocabulary. Several of the corrections targeted concepts I had treated as foundational — substrate agnosticism, the HIL's role, the tool-deterministic constraint box, the biological analogy, the unified equation as reasoning method — but which had not made it onto the README surface despite being present throughout the project record. Session state alone had been insufficient to surface them; canonical resources were where the truth lived. I introduced a new metacognitive command, `rg`, which means: before producing new output on a named topic, re-read the anchoring resources for that topic — persistent-memory files, canonical project docs, experimental notes, directive files — and name the resources consulted in a one-line preamble.

`rg` is not a replacement for the existing recovery commands. It is narrower than `rt` (wholesale context rebuild after loss) and narrower than `rs` (session-state restore). It is a surgical regain-context-on-named-topic, expected to be invoked routinely before significant writing work rather than only on recovery. The fact that the command needed to exist is itself a project finding. The surface that a reader encounters first is the surface most vulnerable to drift, because the session that produced the underlying work is rarely the session that writes the public document. Naming the drift is the first step toward correcting it.

## Closing Reflection

There is something almost ironic in the possibility that a meaningful slice of expert method — constraints, standards, review logic, failure modes, escalation rules — might be encodable in a space no larger than an old-school 3.5-inch floppy disk. Perhaps that image carries weight for me because it mirrors my own entry into computing: when I first engaged meaningfully with this world in the mid-1990s, floppies were still everywhere, and one of the first systems I owned was an IBM 386 clone. Set against today's vast and increasingly (and impractically) extractive datacentre paradigm, the contrast is striking. It points to a different way of thinking about capability: not only as a function of scale, but as a function of how well expertise can be encoded, benchmarked, exchanged, and improved. In that sense, for me, the circle has been closed. What once looked like a limitation of old machines, now reappears as a clue about the future of intelligence systems, where structure may matter as much as scale.
