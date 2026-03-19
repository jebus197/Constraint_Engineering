# Constraint Engineering

**Constraint-Driven Synthesis and Falsification (CDSFL)** is a methodology for making AI-assisted technical work more reliable.

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
- **Tier 2** — confer/defer for domain expert: a single human domain expert reviews machine findings, confers (agrees) or defers (escalates)
- **Tier 3** — confer/defer for external peer review: third-party reviewers with no prior involvement, for high-assurance, safety-critical, or validation contexts

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

The human operator's role is to define the problem box, identify the relevant constraints, monitor for breakout, and escalate when the system reaches the edge of its competence. If the operator cannot bound the problem properly, the model cannot reliably save them.

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

## What this repository contains

- **`README.md`** — operational front door
- **[`PAPER.md`](PAPER.md)** — canonical technical statement
- **[`docs/EXTENDED_RATIONALE.md`](docs/EXTENDED_RATIONALE.md)** — general-audience companion and broader scientific framing
- **[`docs/MATHEMATICAL_APPENDIX.md`](docs/MATHEMATICAL_APPENDIX.md)** — mathematical extensions and calibration path
- **[`docs/FOUNDERS_NOTES.md`](docs/FOUNDERS_NOTES.md)** — design intent, programme logic, and open questions
- **`bench/`** — benchmark harness, evaluation pipeline, and experiment design
- **`bench/directives/`** — domain-specific constraint configurations

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

*CDSFL v1.0. March 2026.*
