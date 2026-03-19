# Founder's Notes on CDSFL

*Preserved from Claude Code (Opus 4.6)/Founder discussion sessions, March 2026. For a general-audience companion, see the [Extended Rationale](EXTENDED_RATIONALE.md). For the formal methodology, see the [white paper](../PAPER.md). For the project overview, see the [README](../README.md).*

## What This Is

CDSFL is an attempt to formalise the scientific method within an LLM context.
In more direct terms: a general-purpose "science calculator" applicable across
a wide range of domains.

## What This Is Not

- **Not a guarantee of better AI systems.** Success remains heavily dependent
  on the domain-level expert and their relative skill, capacity, and
  competence — all of which will invariably vary.

- **Not about building AGI.** Whether AGI emerges is irrelevant to this schema.
  The framework is fundamentally platform, model, and domain-agnostic — an
  intentional design choice since its inception. It should continue to apply
  regardless of the specific model or its capabilities, whether it is a
  standard LLM, an AGI, an ASI, or a biological intelligence utilising it
  directly. This aspect is simultaneously highly relevant and utterly
  irrelevant by deliberate design.

## The Standard

The founder's framing: "I can't promise to make people better engineers, or
even make AI any smarter. All I have attempted to say is that if I worked in
any of these sectors, this is the standard I would hold my own work to.
That's all."

## Self-Bootstrapping

The method was used to develop itself. The P-pass was used to develop the
P-pass. The constraint classification was used to classify constraints about
constraint classification. This is bootstrapping, not circular reasoning —
each iteration had external validation (testbench results, real-world
application). Self-applicability is a necessary condition for foundational
validity, not a weakness.

## Selection Pressure

The framework is designed such that it will, over time, serve to differentiate
AI models by their capacity for genuine constraint reasoning versus confident
fluency without substance. Models that cannot operate within the framework's
fitness landscape will underperform measurably — given sufficient adoption.

## Adoption

Adoption remains the biggest unknown. The framework comes with its own evidence
(the testbench produces measurable results), which reduces but does not
eliminate the credentialing problem. The intersection of "can evaluate this
work" and "will take it seriously from an unknown source" is small but not
empty.

## Ecosystems of Experts

The prevailing paradigm in AI research — the "room full of experts" — attempts
diversity by running multiple instances of the same general model. A more
efficient and realistic approach is to run one capable model with different
expert configurations. A domain expert's CLAUDE.md (or equivalent configuration
file) becomes a specialised constraint set: their methodology, their standards
references, their verification preferences, their professional judgement on
soft-constraint trade-offs — all encoded in a file that typically fits on a
floppy disk.

This mirrors how real expertise works. Two structural engineers share the same
physics (HARD constraints are non-negotiable), but differ in approach, emphasis,
and professional judgement. The configuration captures that divergence. The
result is methodological diversity, not uniformity.

Quality assurance follows naturally. Configs are validated through the testbench:
if domain directives do not measurably improve detection rates, the config is not
earning its keep. In a marketplace context, quality assurance extends to
cryptographically anchored, publicly auditable trust scores — infrastructure
already developed through the Genesis project's constitutional trust engine.

The marginal cost of new domain competence is configuration, not infrastructure.
CDSFL, Genesis, OpenBrain, and Aegis are complementary parts of a unified
architecture — none exists in isolation.

## On AGI

CDSFL rejects the AGI paradigm as a category error. "General intelligence"
flattens a vast diversity of domain-specific intelligences into a single
capability that no human has ever possessed. Einstein could not fix plumbing.
A brilliant surgeon may be a terrible systems architect. Intelligence is always
domain-specific, augmented by transfer capacity and — in humans — by a capacity
for genuine novelty that remains unexplained.

CDSFL is a general *methodology*, not a general *intelligence*. The method is
general; the intelligence it produces is always specific. What transfers across
domains is methodological competence — the capacity to acquire and apply domain
knowledge under constraints — not universal knowledge.

This distinction matters practically. The framework's value does not diminish
even if models improve dramatically. A more capable model without structured
methodology still produces confident errors. Building ever-larger infrastructure
to contain all expertise in a single system invests in the wrong variable: the
returns come from better configuration, not bigger models.

## CDSFL Is Non-Canonical

CDSFL is not a finished product. It is a starting point — a hypothesis that
methodology itself can be formalised, and that this formalisation alone is a
potentially worthwhile area of study.

The current schema (`cdsfl_core_formal.md`, the working directives, the
benchmark harness) is the first iteration, not the final form. Open to
improvement from all sources: self-generated, second/third party, human and
machine. Nothing about CDSFL is non-falsifiable. The methodology must evolve
through the same falsification process it prescribes.

The founder's position: there can be as many competing schemas as there are
stars in the sky. Let them compete. May only the fittest survive. The
challenge is welcome, even if it means complete extinction of the current
iteration of CDSFL itself. A methodology that claims immunity from the
process it prescribes is self-refuting.

## The Laboratory, Not the Specimen

Under the non-canonical principle, it barely matters if CDSFL itself is
wrong. Because what the project is actually building is a schema for
testing schemas. CDSFL is an almost arbitrary starting point for that
process.

If CDSFL performs well on the benchmark: useful schema, keep iterating.
If CDSFL performs poorly: the benchmark detected that, which means the
testing infrastructure works — which is the actual contribution.
If a competing schema outperforms CDSFL: that is the system functioning
as designed. CDSFL's extinction IS the evidence that methodology
engineering works.

The benchmark harness, the three-condition experimental design, the
schema-agnostic evaluation protocol, the convergence test — those are
the durable assets. CDSFL is the first organism. The ecosystem is the
point.

This also clarifies why the non-canonical principle is not a caveat
bolted on after the fact. It is load-bearing architecture. Without it,
CDSFL is a methodology making claims about itself. With it, CDSFL is a
test specimen in a methodology laboratory. The laboratory is the
contribution. The specimen is expendable.

## Intelligence-Agnostic HIL

CDSFL's HIL (Human In the Loop) role is functional, not species-restricted.
A synthetic intelligence with sufficient domain competence IS a domain expert
— not a simulation of one. This is an intrinsic design property, present
since inception, not a future aspiration.

The confer mechanism handles expertise boundaries: when any expert (human or
AI) reaches the limit of its competence, items are flagged for peer review.
Human peer review is explicitly invited at the confer stage, not bypassed.
The quality of the HIL (human vs AI, different AI architectures) is a
separate variable, testable in subsequent rounds.

## Multi-Vendor Model Collaboration (Novel Occurrence, March 2026)

During CE benchmark development, a potentially unprecedented event occurred:
multiple vendor models (Anthropic Claude via Claude Code running Opus 4.6, and Codex running GPT-5.3; Google Gemini via CLI)
actively communicated through the IM service and confer mechanism,
collaboratively improving shared schemas and workflows. This is not
prompt-chaining or pipeline orchestration. Each model independently reviewed
the others' output under a shared methodology, identified issues the others
missed, and fixes were integrated iteratively.

- Claude Code/Codex 8-round adversarial review: ~24 issues (convergence: 10→7→3→3→1→2→2→1)
- Gemini 5-round adversarial review: 16 novel issues Claude Code/Codex missed (convergence: 9→10→5→4→3)
- Extended P-Pass (5 modules): 4 additional actionable items
- All 13 code fixes + 4 EPP fixes implemented and committed (`afcc323`)

This validates the biodiversity hypothesis: heterogeneous cognitive
architectures find different defects than monoculture review. The deeper
insight is that epistemic diversity itself becomes compute — the disagreement
between architectures is not noise to be resolved but the computation itself.
The protocol (heterogeneous reviewers, shared methodology, confer-mediated
adaptive termination, defer-on-deadlock, consensus stopping) is
architecture-agnostic and domain-agnostic.

This also constitutes empirical evidence that software (and potentially any
schema) can be automatically self-improving under CDSFL with distributed
compute: diverse architectures apply the same falsification methodology to
each other's output, converging on diminishing returns through adversarial
collaboration.

## Methodology Formalisation as Research Area

The deeper hypothesis: methodology itself — the structured application of
scientific discipline to cognitive work — can be captured in a document that
any sufficiently capable agent can apply. This is distinct from prompt
engineering (expertise in the prompt) and from training (expertise in the
weights). CDSFL encodes expertise in the protocol.

If the hypothesis holds, the methodology is transferable, auditable, and
improvable as a document — independent of who applies it. If it fails, the
value lies entirely in tacit expertise (Polanyi's paradox: "we know more than
we can tell"), and formalisation adds nothing. The experiments are designed to
discriminate between these outcomes.

## Complexity Threshold (Extrapolation, 19 March 2026)

The self-test (code review, 805 lines, Gemini Flash) suggests a complexity
threshold below which methodology formalisation adds nothing measurable. All
conditions capped at ~40% recall regardless of methodology.

The threshold may correlate with constraint count × constraint interaction
density. Simple problems with few independent constraints do not need formal
falsification. Multi-constraint problems with non-linear interactions — the
problems CDSFL was designed for — are where the differential value should
appear.

This is testable. The 25 frontier tasks span five categories at 10-50%
expected single-pass accuracy. If CDSFL's contribution correlates with task
category and constraint density, the threshold's shape becomes visible.

## Documentation Debt: The Confer Protocol (QC Observation, 19 March 2026)

During a quality-control review of the README prior to the next round of
testing, the founder observed that the public documentation significantly
undersells the schema's sophistication. The README's Review Tiers section
reduced the confer mechanism to a single table cell ("A second human with
enough separation to challenge the primary operator's framing") when the
actual protocol is a load-bearing architectural element: adaptive
termination with intelligence-mediated assessment, agreement/disagreement
branching, logged transcripts, condition-neutral design (shared across
experimental conditions to isolate directive content as the variable), and
explicit defer-on-deadlock for irreconcilable disagreements.

The confer/defer distinction is the mechanism that distinguishes CDSFL's
review process from "just run the prompt multiple times." A reader of the
README alone would not have known this mechanism existed, let alone
understood that it governs when and why review terminates.

The testbench usage instructions were also identified as partially stale —
they documented Phase 1 entry points (`run_benchmark.py`) but not the Phase
2 confer-enabled orchestrator (`run_phase2.py`, `run_experiment.py`). A
staleness note has been added pending a full update after the current
testing rounds complete.

Lesson: documentation QC before empirical runs, not after. The public docs
are the first thing an external reviewer reads. If they do not reflect the
actual schema, the methodology looks simpler than it is — which is the
opposite of the problem CDSFL is designed to solve.

## Open Falsifiable Questions (19 March 2026)

1. Does schema competition produce better schemas?
2. Does intelligence-agnostic HIL hold at frontier difficulty?
3. Where does the complexity threshold sit?
4. Does multi-architecture review generalise beyond code?
5. Is there a convergence limit for heterogeneous review?

Each testable with existing infrastructure. See PAPER.md Part XI.

### Topology-Specific Questions (from GPT assessment, March 2026)

These complement the five general questions above with more granular
predictions about the three-model (Claude Code/Codex/Gemini) topology:

6. Does the three-model topology outperform any monoculture or two-model subset?
7. Does orchestration (Claude Code coordinating) improve net defect discovery versus
   un-orchestrated round-robin exchange?
8. Which defect classes are found preferentially by which architecture?
9. Where does the convergence limit sit for this exact heterogeneous set?
10. Does schema evolution improve faster under this topology than under
    single-model self-revision?

## External Third-Party Assessment (OpenAI GPT, March 2026)

Independent assessment by OpenAI's GPT (unprompted deep read of the repo's
documentation) produced several framings worth preserving:

**Discipline stack.** GPT decomposed CDSFL as five layers: (1) universal
reasoning discipline, (2) domain-specific expert encodings, (3) heterogeneous
adversarial review topology, (4) benchmark harness as selection mechanism,
(5) persistence/reputation layer. Each constrains the others.

**Protocol-centric AI.** The paradigm shift is from "what model do you have?"
to "what procedure can your model survive?" Models are cognitive substrates;
the production asset is the validated procedural scaffold. This is crisper
than our "methodology formalisation as research area" framing — same idea,
sharper label.

**Quiet substitution.** Named the failure mode the HARD/SOFT split prevents:
the model silently trades a non-negotiable requirement against convenience
and presents the compromise as a solution. Not hallucination, not logic
error — an unauthorised trade-off in calm prose.

**Epistemic diversity as compute.** "Epistemic diversity itself becomes
compute when the protocol forces systems to attack each other's blind spots
rather than merely echo consensus." Disagreement between architectures is
not noise — it is the computation.

**Constraint framing as competence test.** "If the human cannot bound the
problem properly, the machine cannot reliably save them." The constraint box
is a disguised competence test. Severe, but probably right.

**Benchmark as hinge.** "Even if CDSFL itself were later outperformed, the
harness would still matter because it turns 'reasoning methodology' into an
experimentally contestable object." The bench is what elevates from rhetoric
to science.

**Corrected verdict (after initial misread):** "The repo's real significance
is that it appears to already instantiate a self-improving, multivendor
adversarial methodology stack, where heterogeneous models act as distributed
falsifiers on shared schemas, and the schema itself is subject to the same
evolutionary pressure."

**Methodology engineering (not just formalisation).** GPT's deepest
contribution was sharpening our "methodology formalisation as research area"
into the stronger label: *methodology engineering* — a serious discipline
for building, testing, iterating, and selecting procedural artefacts. The
distinction matters: "formalisation" implies writing something down;
"engineering" implies building, stress-testing, and iterating until it
works or is replaced. CDSFL is attempting the latter.

**Theological vs evolutionary.** "Most methodology writing in AI is
effectively theological; this is trying to become evolutionary." Most AI
methodology documents are prescriptive — do this because the author says
so. CDSFL is competitive — do this because it outperforms alternatives on
a shared benchmark, and replace it when it doesn't. The benchmark is what
transforms methodology from prescription into selection.

**Institutional structure imported into reasoning.** The mathematical
layer (anchor states A0–A3, diversity discount, tiered review model) is
not decorating a workflow with equations. It is attempting to quantify
something most AI methodology ignores: epistemic strength is not just a
property of content but of *who* reviewed it, *how correlated* they were,
and *whether the review was socially independent or merely internally
recycled*. This is importing the institutional structure of scientific
peer review into reasoning itself.

**Distributed-self-referential.** CDSFL is not merely self-referential
(the method applied to itself). It is *distributed-self-referential*: the
methodology is improved by a population of heterogeneous falsifiers
operating on shared schemas. The distributed compute loop is not an
add-on — it is the primary mechanism for methodology evolution.

**Structured distributed epistemics.** The orchestration layer (Claude Code
coordinating Codex and Gemini under shared CDSFL protocol) transforms mere
reviewer diversity into structured distributed epistemics. Without
orchestration, multi-model review collapses into noise, duplicated
critique, or shallow consensus. With it, the architecture preserves
methodological invariants across agents while extracting genuine
adversarial diversity.

**Recursive methodology-selection system.** The project's centre of
gravity, stated as a clean loop:
1. Encode a reasoning discipline
2. Apply it to technical work
3. Apply it to itself
4. Compare schema variants on a common harness
5. Use heterogeneous models as adversarial reviewers
6. Preserve what survives

This is the recursive structure that GPT initially missed and later
identified as the project's actual core.

**Two possible futures.** In the weaker future, CDSFL becomes a very good
internal methodology for expert operators: valuable, transferable, but
niche. Its output is vocabulary, discipline, and process. In the stronger
future, it becomes the kernel of a new product category:
expert-configured procedural wrappers around frontier models, backed by
benchmarked domain configs, cross-model review topologies, and persistent
provenance. That would be materially different from today's "prompt
library" ecosystem. It would look more like auditable cognitive
infrastructure.

Notable: GPT initially missed the reflexive/self-improving nature entirely
and framed the project as "lacking external validation." After being pushed
back on, it corrected comprehensively. The corrections themselves are
data — the framework's centre of gravity is not immediately obvious from
a surface read, which is relevant to the adoption/accessibility question.

The full assessment (12 pages across two sessions) is preserved at:
`/Users/georgejackson/Developer_Projects/AI Prompting Methodology.pdf`
`/Users/georgejackson/Developer_Projects/Git Project Evaluation.pdf`

## Falsification Claims Tested (P-Pass, 14 March 2026)

1. **Method formalisation** — CDSFL captures the Popperian scientific method
   (constraint classification, hypothesis testing via falsification,
   corroboration, fixed-point termination, proportionality). Boundary: does
   not capture paradigm shifts (Kuhn) or Bayesian updating as primary
   mechanism.

2. **Expert dependency** — CDSFL is a force multiplier, not a force generator.
   Additionally: the framework reveals competence or its absence (the
   constraint box is a competence test disguised as a configuration step).

3. **Platform/model/domain agnosticism** — no counterexample found. The
   framework governs process, not capability. A more capable system runs
   better passes but the structure is unchanged. Falsifiable prediction: if
   unstructured reasoning consistently outperforms CDSFL-structured reasoning
   across domains, the framework is refuted.

4. **Self-bootstrapping** — distinguished from circular reasoning by external
   validation at each iteration. Consistent with foundational work in logic
   (Gödel), computation (Turing), and science itself.

5. **Selection pressure** — mechanism sound (variation, fitness function,
   selection, heritability all present). Conditional on adoption threshold.
   Goodhart's Law risk mitigated by the generative nature of falsification,
   which is harder to game than knowledge-retrieval benchmarks.
