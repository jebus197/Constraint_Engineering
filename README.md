# CDSFL: Constraint-Driven Synthesis and Falsification

A methodology for making AI-assisted technical work more reliable.

Large language models can be useful engineering assistants. They can also produce polished, confident output that is physically impossible, logically inconsistent, legally non-compliant, or silently outside scope. In non-trivial work, the central problem is not only model capability. It is method.

CDSFL addresses that problem by forcing machine-assisted reasoning into a more scientific discipline: generate a solution, try to break it, fix what fails, then try to break the fix. Trust is not granted to the first answer. It is earned by what survives falsification.

This repository is therefore not just a prompt pack. It is an attempt at **methodology engineering**: building, testing, and improving procedural scaffolds for technical cognition under empirical pressure.

## The core idea

The central mechanism is the **P-Pass** — a Popperian falsification pass.

1. Generate the best available answer.
2. Actively try to break it.
3. Fix what fails.
4. Try to break the fix.
5. Repeat until further passes yield genuinely diminishing returns, or the unresolved issue is outside the current scope.

The user should not see the model's first draft. The user should see what remained after adversarial scrutiny.

For multi-module systems, CDSFL extends to the **Extended P-Pass**: modular review followed by a fresh-context adversarial pass aimed specifically at interface failures, emergent contradictions, and hidden shared assumptions.

## Why this is needed

Current models fail in predictable ways under technical load:

- they optimise for fluency and helpfulness more strongly than strict technical truth in open-ended generation;
- they present weak inference and hard fact in the same certainty register;
- they forget prior falsification work between sessions unless that work is explicitly preserved.

The result is systematic overconfidence. A model may produce a circuit that cannot work, a design that violates non-negotiable constraints, or a governance structure that contradicts itself — all with calm, professional prose.

CDSFL exists to make that failure mode harder to survive.

## What CDSFL adds beyond "run it again"

### 1. Constraint classification

Every constraint is classified as either:

- **HARD** — physics, mathematics, law, safety, explicit absolutes; or
- **SOFT** — convenience, cost preference, ergonomic preference, and other negotiable trade-offs.

Ambiguous cases default to HARD.

This prevents **quiet substitution**: the model silently trading away a non-negotiable requirement to produce a more pleasing answer.

### 2. Epistemic marking

Only two uncertainty markers surface in output:

- **`[VERIFY:current]`** — the claim depends on current external state;
- **`[SPECULATIVE]`** — the claim is structurally plausible but not yet empirically grounded.

The aim is not to flood the user with generic confidence language. It is to identify what actually requires action.

### 3. Tiered review

CDSFL does not assume every task should jump from one model directly to formal peer review. It uses a four-tier review ladder, with all tiers overseen by a human domain-level expert who controls and adjudicates the process:

- **Tier 0** — individual machine P-pass: a single machine performing adversarial self-review (default for every task)
- **Tier 1** — adversarial multi-machine P-pass: two or more machines, the number and composition determined by the domain operator, reviewing each other's output until diminishing returns are reached
- **Tier 2** — confer/defer for domain expert: a single human domain expert conducts their own independent falsification — using a formal method of their choosing — against the machine findings, then confers (agrees) or defers (escalates)
- **Tier 3** — confer/defer for external peer review: third-party reviewers with no prior involvement conduct independent falsification, for high-assurance, safety-critical, or validation contexts

When reviewers at any tier reach irreconcilable disagreement, items are explicitly deferred with both positions recorded rather than forced to false consensus.

### 4. Persistence and verification

If falsification improves reasoning, the result of falsification should not vanish at session end.

CDSFL includes a persistence layer intended to preserve claims, revisions, and reasoning checkpoints with cryptographic integrity. Its purpose is not to prove that a conclusion is true. Its purpose is to prove that a record is authentic, untampered, and attributable.

That distinction matters. Provenance is not correctness. But reliable provenance makes low-quality reasoning harder to recycle and strong reasoning easier to audit over time.

## The mathematical framework

The white paper presents the methodology at two levels.

For intuition, CDSFL uses a simple corroboration model:

**C(n) = 1 − (1 − p)^n**

If each serious falsification pass has probability **p** of catching a real defect, repeated passes increase the probability that the defect is exposed. The gains diminish. Certainty is never reached. And if **p ≈ 0**, the entire ritual is empty: no number of ceremonial passes produces real corroboration.

For technical readers, the white paper extends this into a structured operational model:

**F_n = Σ_k w_k [1 − Π_i (1 − d_i · p_ik)]**

This captures three realities that the scalar model cannot:

- different flaw classes matter differently;
- different passes are better at detecting different flaw types;
- repeated reviews are correlated, so apparent independence must be discounted.

Anchor states then separate internal falsification from stronger external validation:

- **A0** — internal only
- **A1** — cross-agent verification
- **A2** — human expert review
- **A3** — independent replication

The mathematical appendix extends the formalism further with residual risk, class-specific diversity discounts, parameter uncertainty, and safety-critical severity separation. These extensions are stated precisely so they can be tested and discarded if they fail to improve predictive performance.

## The human role

CDSFL does **not** make novices into experts.

It is a **force multiplier, not a force generator**.

The human operator's role is to define the problem box, identify the relevant constraints, monitor for breakout, escalate when the system reaches the edge of its competence, and — at the review tiers — conduct their own independent falsification rather than passively approve machine output. If the operator cannot bound the problem properly, the model cannot reliably save them.

This is not an afterthought. It is one of the methodology's central design choices.

The framework also treats the expert role as **functional rather than species-bound**: a sufficiently capable synthetic system can, in principle, occupy the expert role. But its competence still has to be demonstrated rather than assumed.

## Why the benchmark matters

Without a shared testbench, methodology degenerates into preference.

CDSFL therefore includes a schema-agnostic benchmark harness built around three conditions:

- **Control** — raw model output
- **Experimental** — full CDSFL
- **Calibration baseline** — structured iteration without the full CDSFL discipline

That design isolates three questions:

1. Does the full methodology outperform bare output?
2. Does structured iteration alone help?
3. Do the specific CDSFL disciplines matter beyond generic caution?

This is why CDSFL is explicitly **non-canonical**. If another schema performs better on the same harness, the correct response is adoption, not defence. The durable contribution is not only CDSFL as a specimen, but the laboratory for testing specimens.

## Multi-architecture review and the biodiversity claim

One of the strongest claims in the current project is that **heterogeneous review matters**.

During development, different model families identified defects that prior monoculture review had missed. The implication is that epistemic diversity can function as compute: different cognitive architectures attack different blind spots.

That moves the focus away from "which single model is best?" and toward "what procedure can a model survive, and what complementary architectures improve coverage?"

## The method applied to itself

On 27 March 2026, the CDSFL mathematical model was subjected to its own distributed compute protocol. A precursor blind pass found eleven genuine errors, which were corrected. Three models then ran the first fully functional distributed compute round — each operating under the full CDSFL core directives as system prompt, producing independent structured output for the project manager to synthesise. Five design decisions were resolved, two proposed additions were unanimously rejected on mathematical grounds, and a third was accepted with modifications.

The most unexpected finding was not mathematical. The project manager model — which coordinated the review but did not operate under the CDSFL framework — was able to evaluate reasoning it could not have generated, because the framework-guided models produced output in a structured format that separated verdict from evidence, evidence from proposed change, and proposed change from self-criticism. This suggests the framework may function as a **communication protocol** as much as an analytical protocol: it makes high-quality analysis accessible to decision-makers who cannot perform the analysis themselves, provided they can follow a structured argument. Whether this generalises to human decision-makers is a [falsifiable prediction](docs/EXPERIMENTAL_RESULTS.md) that has not yet been tested.

## Four cognitive modes and the dynamic management layer

When four models independently formalised six areas of the CDSFL management layer (28 March 2026), operating under identical system prompts with no sight of each other's work, the outputs diverged not in quality but in kind.

One model generated and falsified in a single coupled process — the self-objections appeared inline, not as an afterthought. Another found the operational gaps: every unique contribution addressed a failure mode the mathematical formulation alone would miss. A third compressed — achieving the highest reduction property density relative to output length, consistently seeking mathematical tightness, sometimes at the expense of robustness. A fourth was the only model that visibly self-corrected mid-output — six times, once per area — arriving at the consensus by trying something simple, recognising why it was insufficient, and correcting. The most clearly Popperian process in the group, by a model that looked weakest on raw metrics.

These four cognitive modes — deep architecture, engineering pragmatism, mathematical compression, and iterative refinement — appear to be complementary rather than redundant. The dynamic management layer (`bench/dynamic_management.py`, ~3,400 lines, 27 classes) was built from the converged output of this experiment. It implements adaptive routing: each model receives work matched to its demonstrated strengths, based on a four-dimensional capability fingerprint (decay rate, verification score, total findings, coverage) that updates from observed performance rather than declared capability. The design principle is older than computing: there is no such thing as a useless contributor, only a misallocated one.

## Live orchestration: Experiment 12

On 29 March 2026, the dynamic management layer managed itself for the first time. Five models reviewed their own management code — 3,181 lines — through the system those classes implement. Twenty rounds. 809 findings. And every convergence detector broke.

The convergence metric sat at zero for every round because lexical similarity cannot detect that two different phrasings describe the same finding. The marginal value metric oscillated because losing a model to context overflow reduced round cost while finding count held steady — the system interpreted attrition as improved productivity. The stop predicate never fired. Five models started; only two survived to round 20, the rest progressively blocked by context accumulation. The experiment ran to its arbitrary limit because no instrument could terminate it.

Despite the broken termination, the experiment produced genuinely useful data. The dominant model (337 findings, all 21 rounds) showed vocabulary novelty declining from 23.9% to 7.7% — genuine diminishing returns confirmed by cross-round vocabulary overlap analysis showing two-thirds of late-round terminology absent from early rounds. Not churn. Genuine exploration of progressively more marginal territory. The only statistically significant quality trend across eight tests was one model's severity improvement (p=0.006), which has a critical confound: it received richer context in later rounds, so the improvement may be environment-mediated rather than intrinsic. The self-improvement prediction — that models improve under CDSFL — is not confirmed by this data. What is confirmed is that the *system's output* improves across rounds, through accumulated context rather than model capability change. CDSFL improves the input to each model, and the model responds accordingly. Whether that is a weaker or stronger claim than intrinsic improvement is a matter of perspective.

The experiment's most valuable output was the diagnosis: three independent convergence detectors, each designed from different mathematical principles, all failed simultaneously for different reasons. Seven fixes were formalised and committed: a vocabulary saturation stop signal (similarity-independent), a windowed fingerprint replacing the collapsing exponential moving average, model restart logic, per-model adaptive decomposition, artifact-size-based round scaling, and an immune response layer that monitors the health of the detection instruments themselves. Whether these fixes work is the subject of Experiment 13.

## Toward the configured synthetic domain expert

The project's trajectory, viewed across 15 days and 12 experiments, is not toward a better chatbot. It is toward a **configured synthetic domain expert**: a system whose competence arises from the joint action of encoded method, iterative expert interaction, self-monitoring, computational verification, policy governance, and cryptographic accountability.

That phrase requires unpacking. Method without verification is unverified discipline. Verification without method is calculation without direction. Both without governance are unbounded. All three without decay diagnostics cannot tell analysis from churn. None of them without accountability produce durable responsibility. These are not independent improvements. They are a stack, and the competence claim is distributed across the stack rather than residing in any single layer.

The distinction from conventional AI tooling is structural. A chatbot gives output and leaves the user to decide whether it sounds right. A system built on this architecture produces a decay curve, a verification score, a coverage metric, a trust trajectory, and a permanent record — so that the user is not left relying only on rhetoric or intuition. The centre of gravity shifts from plausible performance to measurable analytical behaviour. Whether that shift justifies the engineering cost is an empirical question. The experiments are designed to answer it.

The deeper hypothesis is that **expertise itself can become a tradable engineered artefact**. If expert encodings — methodology, domain standards, failure recognitions, review preferences, escalation logic — can be captured in portable configurations, benchmarked against a shared harness, cryptographically anchored, and improved over time, then the critical unit is no longer only model weights. It is a composed system of method plus verification plus governance. The marginal cost of new domain competence shifts from "who has the biggest model?" toward "who can encode, test, refine, and combine expertise most effectively?" Whether that shift is real or aspirational is precisely what the next round of experiments will test.

Full experimental data, including methodology, raw results, and caveats, is recorded in [`docs/EXPERIMENTAL_RESULTS.md`](docs/EXPERIMENTAL_RESULTS.md). The distributed compute rounds are documented in the [white paper](PAPER.md) (Part XIV) and discussed in the [founder's notes](docs/FOUNDERS_NOTES.md). The broader implications — for mixed human-AI teams, for non-specialist decision-makers, and for the framework's role as a transparency mechanism — are explored in the [extended rationale](docs/EXTENDED_RATIONALE.md).

## What this repository contains

- **`README.md`** — operational front door
- **[`PAPER.md`](PAPER.md)** — canonical technical statement
- **[`docs/EXTENDED_RATIONALE.md`](docs/EXTENDED_RATIONALE.md)** — general-audience companion and broader scientific framing
- **[`docs/MATHEMATICAL_APPENDIX.md`](docs/MATHEMATICAL_APPENDIX.md)** — mathematical extensions and calibration path
- **[`docs/FOUNDERS_NOTES.md`](docs/FOUNDERS_NOTES.md)** — design intent, programme logic, and open questions
- **[`docs/EXPERIMENTAL_RESULTS.md`](docs/EXPERIMENTAL_RESULTS.md)** — empirical results, including null findings and failures
- **`bench/`** — benchmark harness, evaluation pipeline, experiment design, and dynamic management layer
- **`bench/dynamic_management.py`** — dynamic management and load-balancing layer (~3,400 lines, 27 classes)
- **`bench/run_exp12_live_wire.py`** — live orchestration engine for multi-model experiments
- **`bench/verification_chain.py`** — tamper-evident persistence layer (RFC 9162 Merkle trees, hash chains, optional Ed25519)
- **`bench/directives/`** — domain-specific constraint configurations (10 domains, 28 directive files)
- **`bench/cdsfl_registry/`** — Constraint Editor (CE): hierarchical policy engine for configuration governance
- **[`configs/`](configs/)** — domain expert configurations: portable, reusable cognitive encodings with examples and templates (see [`configs/README.md`](configs/README.md))
- **[`resources/`](resources/)** — project onboarding and recovery: everything needed to pick up the project from scratch, reproduce results, or attempt to refute them (see [`resources/ONBOARDING.md`](resources/ONBOARDING.md))

## Quick start

```bash
cd bench
pip install -r requirements.txt
python3 run_benchmark.py --dry-run
python3 run_benchmark.py --output results.json
python3 evaluate.py results.json --output evaluation.json
python3 report.py evaluation.json --csv evaluation.csv
```

Use the benchmark to answer the only question that ultimately matters:

**Does this procedure measurably improve technical work on the tasks you care about?**

## Known boundaries

CDSFL has clear limits.

- It does **not** solve the ground-truth problem.
- It does **not** prevent a model from confidently surviving its own internal review when reality is absent.
- It does **not** apply cleanly to aesthetics, ethics, or pure preference.
- It does **not** remove the need for competent operators.
- It does **not** turn persistence into proof of correctness.
- Its broader claims still require wider empirical testing.

Those limits are part of the method, not an embarrassment to be hidden. A methodology that cannot state its boundaries is not ready for technical use.

## Why this may matter beyond software

Software engineering was the accessible starting point, not the natural limit of the framework.

The method is intended for any domain where:

- claims can be falsified,
- constraints can be stated,
- hidden contradiction matters,
- and being wrong has real downstream cost.

That includes engineering design, mathematics, scientific modelling, formal verification, systems architecture, and potentially other technical fields where disciplined elimination matters more than rhetorical fluency.

The deeper hypothesis is that parts of scientific and engineering method can be formalised into a portable, testable, auditable protocol — and that doing so may become a research area in its own right.

## One-sentence summary

**CDSFL is a falsifiable methodology for forcing AI-assisted technical work into a more scientific discipline: generate, try to break, preserve what survives, and replace the method itself if a better one wins.**

MIT licensed. See [LICENSE](LICENSE).

*CDSFL v1.1. 29 March 2026. 12 experiments, 5 models, ~3,400 lines of management infrastructure, 173 tests.*
