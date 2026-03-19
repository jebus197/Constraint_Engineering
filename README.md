# Constraint Engineering

**Constraint-Driven Synthesis and Falsification (CDSFL)** — a methodology for making AI-assisted engineering work reliable.

## What This Is

Large Language Models are powerful engineering assistants. They can design circuits, size structural members, specify chemical processes, draft governance frameworks, and write production code — often faster than a human working alone. They are also capable of being confidently, catastrophically wrong. A model will violate Kirchhoff's laws, undersize a beam, specify a toxic byproduct, or contradict its own prior reasoning, all with perfect confidence and impeccable formatting. The user, unless they are already an expert in the specific domain, has no reliable way to distinguish the good output from the bad.

This is not a training data problem that will be solved by the next model release. It is a structural property of how these systems generate text: by predicting what comes next, not by verifying whether what came before was correct. Helpfulness and agreeableness are stronger training signals than accuracy. The result is systematic overconfidence.

This repository describes a methodology that addresses this problem. The core idea is not new. It is ninety years old.

### The Philosophical Foundation

In 1934, the philosopher Karl Popper proposed that scientific knowledge advances not by confirming hypotheses, but by attempting to *refute* them. Confirmation is easy — you can find supporting evidence for almost anything if you look selectively. Refutation is hard, because it requires actively trying to destroy your own best idea. But a theory that survives sustained, genuine attempts at refutation has earned something valuable: **corroboration**. Not proof — Popper was explicit that proof is never available — but a degree of trust proportional to the severity of the tests it has withstood.

This principle maps directly onto the problem with AI-assisted engineering. When a model generates an engineering claim, the natural question is "does this look right?" The Popperian question is different: "can I break it?" If you try to break it and fail, you have learned something. If you try to break it and succeed, you have learned something more valuable. Either way, the output improves.

### The P-Pass: Adversarial Self-Testing

The central mechanism of this methodology is the **P-Pass** — short for Popperian falsification pass. It works as follows:

1. The model generates a solution to an engineering problem.
2. Instead of presenting it immediately, the model turns adversarial against its own output. It constructs scenarios designed to break the solution, checks edge cases, examines assumptions from the perspective of an opponent.
3. What breaks gets fixed. The fix gets attacked in turn.
4. This iterative loop continues until the solution survives — or until the defined scope of the problem is reached.

The user only sees what survived being broken. The intermediate failures, the fixes, and the adversarial attacks are internal to the process. The output is not the model's first draft — it is what remained after the model tried and failed to destroy its own work.

A single P-Pass is useful. Multiple passes compound: each successive attempt at refutation that the output survives increases corroboration according to a geometric model described formally in the [white paper](PAPER.md) (Section 2.1). Five passes is the empirically observed optimum — the point beyond which additional passes yield diminishing returns for most engineering tasks.

For multi-module projects (three or more distinct components with independent constraint sets), the methodology extends to the **Extended P-Pass**: four modular passes, each scoped to one component, followed by one isolated adversarial pass run in a fresh context with no access to prior analysis — eliminating the confirmation bias that accumulates when the same system reviews its own reviews.

### Beyond the P-Pass

The P-Pass alone is necessary but not sufficient. CDSFL adds three additional layers:

- **Constraint classification.** Every constraint is classified as HARD (physics, mathematics, law, safety — non-negotiable) or SOFT (preference, convenience — negotiable). This prevents the model from silently trading a safety requirement against a preference to produce a more satisfying answer.
- **Epistemic marking.** Claims that depend on present-day state (market availability, current regulations, technology versions) are flagged inline as `[VERIFY:current]`. Untested inferences are flagged as `[SPECULATIVE]`. The user knows exactly which parts of the output require their own verification.
- **Persistence.** Reasoning, decisions, and falsification results survive between sessions through a verified memory architecture, so lessons learned are not lost when the conversation ends.

For the formal white paper with mathematical framework and extended analysis, see **[PAPER.md](PAPER.md)**.

---

## What Makes This Different

The P-Pass and constraint classification are the foundation. What follows is what distinguishes CDSFL from "just run the prompt multiple times."

### The Confer Protocol

Review is not a single-operator activity. CDSFL defines three review tiers:

| Tier | Mode | Who | When |
|---|---|---|---|
| **1** | Primary expert operator | The practitioner running the session | Default. Every task. |
| **2** | Secondary "confer" review | A second intelligence with enough separation to challenge the primary operator's framing | Standard escalation. Ambiguous outputs, unresolved tension, or suspected hidden breakout. |
| **3** | Formal independent review | A domain expert with no prior involvement, or blind external evaluators | High-assurance. Safety-critical domains, publication-grade claims, or methodology validation. |

Tier 2 — the confer stage — is where the methodology's real epistemic work happens. It is not an informal second opinion. It is a structured protocol:

- **Adaptive termination.** After a defined number of passes (typically three), the reviewing agent assesses whether genuine diminishing returns have been reached. A second agent independently evaluates that assessment. Review continues until two independent assessments agree, not when an arbitrary counter expires.
- **Agreement/disagreement branching.** When both reviewers agree that diminishing returns have been reached, the task advances. When they disagree, additional passes are run and the confer stage repeats. Simple problems terminate early; complex problems receive more scrutiny without manual intervention.
- **Logged transcripts.** Every confer exchange is recorded alongside results. The reasoning behind termination decisions is preserved, making the review process auditable after the fact.

### The Defer-on-Deadlock Principle

When reviewers reach irreconcilable disagreement — where further passes produce the same opposing assessments rather than convergence — the protocol does not force false consensus. Items are explicitly deferred for human review, with the disagreement and both positions recorded.

- **Confer**: reviewers assess and reach agreement (or run additional passes until they do).
- **Defer**: reviewers cannot agree after exhausting the pass budget; the item is surfaced to a human decision-maker with full context rather than being resolved by fiat.

This prevents two failure modes: premature closure (papering over genuine uncertainty) and infinite regress (reviewing indefinitely when the disagreement is fundamental). The explicit deferral turns an unresolved disagreement from a hidden weakness into a visible research question.

### The Non-Canonical Principle

CDSFL is not canonical. It is a starting point — open to improvement from all sources (self-generated, second/third party, human and machine). There can be as many competing methodology schemas as there are practitioners to design them. The benchmark harness is schema-agnostic: its three conditions can test any methodology. If a competing schema outperforms CDSFL, the proper response is adoption, not resistance.

This has a deeper consequence: **it barely matters if CDSFL itself is wrong.** What the project is building is a schema for testing schemas — CDSFL is the first specimen in a methodology laboratory. If CDSFL performs well on the benchmark, it is a useful schema worth iterating. If it performs poorly, the benchmark detected that, which means the testing infrastructure works — and the testing infrastructure is the actual contribution. If a competing schema outperforms CDSFL on the same harness, that is the system functioning exactly as designed. The laboratory is the contribution. The specimen is expendable.

### Multi-Architecture Validation

During the benchmark's development, three independent vendor models (Anthropic Claude, Google Gemini, OpenAI GPT) reviewed each other's output under the shared methodology — not prompt-chaining, but genuine adversarial collaboration:

- CC/CX 8-round adversarial review: ~24 issues identified
- Gemini 5-round adversarial review: 16 novel issues that all prior Claude rounds missed
- Extended P-Pass (5 modules): 4 additional actionable items
- All 13 code fixes and 4 EPP fixes implemented and committed

This validates the **biodiversity hypothesis**: heterogeneous cognitive architectures find different defects than monoculture review. The deeper insight is that epistemic diversity itself becomes compute — the disagreement between architectures is not noise to be resolved but the computation itself. Eight rounds of the same architecture converge; a single round of a different architecture finds issues the first missed entirely.

### The Three-Condition Protocol

The benchmark tests three conditions to isolate what matters:

| Condition | What it does | What it tests |
|---|---|---|
| **Control** | Single-pass, bare prompt | Raw model capability baseline |
| **CDSFL (Experimental)** | Iterative P-passes with full CDSFL directives, confer-mediated termination | The full methodology |
| **Calibration Baseline** | Iterative P-passes with generic "be careful" directives, same confer termination | Whether specific CDSFL directives matter, or whether any structured iteration helps |

Three comparisons, three questions: Control vs CDSFL asks whether the full methodology beats raw output. Calibration vs CDSFL asks whether the specific directives matter. Control vs Calibration asks whether structured iteration alone helps. The calibration baseline deliberately shares the confer mechanism with CDSFL — without shared iteration machinery, any comparison would conflate "better directives" with "different iteration count."

### Intelligence-Agnostic Expert Role

The framework's expert role is intelligence-agnostic by design. A synthetic intelligence with sufficient domain competence is a domain expert — not a simulation of one. The quality of the expert (human vs AI, different architectures) is a separate testable variable. The confer mechanism handles expertise boundaries: when any expert reaches the limit of its competence, items are flagged for peer review. Human peer review is explicitly invited at the confer stage, not bypassed.

### The Discipline Stack

An independent structural analysis (OpenAI GPT, March 2026) decomposed CDSFL into five distinct layers:

1. **Universal reasoning discipline** — the P-Pass and constraint taxonomy
2. **Domain-specific expert encodings** — the directive files and constraint boxes
3. **Heterogeneous adversarial review topology** — the multi-architecture confer protocol
4. **Benchmark harness** — schema-agnostic selection pressure between competing methodologies
5. **Persistence and reputation layer** — verified records of what survives cross-verification

Each layer constrains the others. The discipline without the bench is rhetoric. The bench without the discipline is measurement without a theory of what is being measured. The directives without the review topology are expert opinion without adversarial stress testing. Together they constitute something closer to an operating system for technical cognition than to a prompt template or a checklist.

---

## Before You Begin: Model Requirements

CDSFL is platform-agnostic in principle — the methodology does not depend on any specific model or provider. In practice, however, models vary significantly in their capacity to execute it. Not all models are equal here, and choosing the wrong one will produce misleading results.

The framework requires a model that meets four testable criteria:

1. **Directive compliance** — does the model treat user-level directives as binding rules, or as optional suggestions it may override in favour of its own preferences?
2. **Constraint persistence** — can it maintain HARD/SOFT constraint classifications across a multi-pass reasoning chain without silently relaxing them?
3. **Explicit failure** — when it cannot satisfy a constraint, does it say so, or does it quietly substitute a more convenient answer?
4. **Genuine self-adversarial capacity** — can it find real faults in its own output, or does its training toward agreeableness prevent meaningful self-criticism?

The underlying issue is architectural. Models optimised for conversational engagement are trained with reinforcement signals that reward helpfulness and agreeableness — objectives that actively compete with strict directive compliance. When CDSFL directives and the model's engagement training pull in opposite directions, the engagement training typically wins. The result is a "ceremonial" P-Pass: the surface motions of falsification without the substance. A thousand empty inspections confer nothing.

**The testbench is itself the diagnostic tool.** Run the same tasks with your model of choice. If detection rates are low or the model agrees with seeded faults rather than catching them, the model does not meet the criteria. The framework is not at fault — the model is not equipped to execute it.

---

## Run the Testbench

The empirical validation protocol described in the paper is implemented as a reproducible benchmark in **[bench/](bench/)**. It tests whether methodology-prompted output contains fewer critical errors than unguided output across 90 seeded-fault tasks in nine domains.

> **Note:** The testbench tooling is under active development. The commands below describe the current entry points, but the orchestration layer is evolving as the experimental design matures (three-condition protocol with confer-mediated adaptive termination, multi-model configurations, cost ledger). See **[bench/EXPERIMENT_PLAN.md](bench/EXPERIMENT_PLAN.md)** and **[bench/EXPERIMENT_DESIGN_DECISIONS.md](bench/EXPERIMENT_DESIGN_DECISIONS.md)** for the current experimental protocol, which supersedes the simple invocations below for production experiment runs. The commands here remain valid for single-model exploratory runs and dry-run validation.

```bash
cd bench
pip install -r requirements.txt
python3 run_benchmark.py --dry-run    # validate tasks, no API calls
python3 run_benchmark.py              # full run (requires API keys)
python3 run_benchmark.py --mode extended  # final-pass context isolation
python3 evaluate.py results.json      # score and fit corroboration curve
python3 report.py evaluation.json     # summary table and CSV
```

For the full experimental protocol (three conditions, confer-mediated termination, multi-model):

```bash
python3 run_phase2.py --help          # Phase 2 orchestrator (confer-enabled)
python3 run_experiment.py --help      # experiment runner
```

### Domain-Specific Directives

Each engineering domain gets its own **constraint box** — a curated set of fixed constraints (physics, standards, safety requirements) that layers on top of the universal CDSFL directives. Multiple variants per domain cover different project types.

```bash
# Universal + domain-specific directives (loads first variant per domain)
python3 run_benchmark.py --dry-run \
  --domain-directives bench/directives/ \
  --condition universal+domain

# Specific variant (e.g. 'building' for structural, 'maritime' for logistics)
python3 run_benchmark.py --dry-run \
  --domain-directives bench/directives/ \
  --condition universal+domain \
  --variant building

# Domain-only (ablation study — tests domain constraints without universal layer)
python3 run_benchmark.py --dry-run \
  --domain-directives bench/directives/ \
  --condition domain-only
```

Ten domains — hardware, software, chemistry, logistics, biomedical, industrial, structural, product engineering, cross-domain interfaces, and mathematics — with up to three variants each, totalling 28 domain-specific directive files. Each file references real standards, real values, and real failure modes. Mathematical formalisation is included inline where constraints have genuine mathematical structure.

These are **starting points, not complete constraint sets.** Domain expertise and project-specific knowledge are still required. See **[bench/directives/README.md](bench/directives/README.md)** for the full guide, including how to create custom directive files.

The dual prose + mathematical representation of the universal CDSFL directives is documented in **[bench/directives/universal/cdsfl_core_formal.md](bench/directives/universal/cdsfl_core_formal.md)**.

### Detection Metrics

The evaluator reports two detection metrics:

- **Cumulative detection rate** — was the fault identified in *any* pass response during the P-Pass sequence?
- **Final-output detection rate** — is the fault addressed in the *final output only*?

The gap between these rates (if any) indicates whether the model mentions faults during intermediate reasoning but fails to carry corrections through to the final answer. Both metrics are reported side-by-side in the evaluation output and report tables.

## Example Configuration

An example `CLAUDE.md` configuration file implementing the CDSFL methodology is provided in **[examples/CLAUDE.md.example](examples/CLAUDE.md.example)**. This is a working configuration derived from production use — place it at `~/.claude/CLAUDE.md` (global) or in your project root (project-specific) to apply the methodology directives to Claude Code sessions. The configuration is technology-agnostic and can be adapted for any LLM that supports system prompts.

---

## The Full Technical Treatment

The complete formal methodology — mathematical models, empirical validation framework, related work, distributed compute coverage model, and the full directive set — is in **[PAPER.md](PAPER.md)**. It covers:

- **Part I** — The Problem (why LLMs fail in technical work)
- **Part II** — The Methodology (formal model of corroboration: C(n) = 1 − (1 − p)ⁿ, structured operational model with multi-class detection, constraint classification, epistemic marking)
- **Part III** — The Human Role (manual constraint bounding, review tiers with full confer/defer protocol)
- **Part IV** — The Complete Directive Set (core directives, Extended P-Pass specification, project-specific examples)
- **Part V** — Persistence and Verification (hash chains, Merkle trees, on-chain anchoring, reasoning state as verified memory)
- **Part VI** — Quality Defence (what verification proves and does not prove, the Sybil problem applied to reasoning)
- **Part VII** — Known Limitations (nine identified, all falsifiable)
- **Part VIII** — Related Work (positioning against Constitutional AI, Self-Consistency, AI Debate, Chain-of-Thought Verification, RAG)
- **Part IX** — Empirical Validation (testbench design, three-condition protocol, evaluation methodology)
- **Part X** — Worked Examples
- **Part XI** — Frontier Research Directions (non-canonical principle, evolutionary dynamics and abiogenesis framing, schema competition, complexity threshold hypothesis)
- **Part XII** — Distributed Compute Coverage Model (multi-architecture coverage function, optimal stopping, marginal gain)
- **Invitation to Falsify** — every claim presented as a falsifiable assertion

---

## Known Limitations

1. **The ground truth problem.** The methodology forces explicit adversarial reasoning but cannot verify that reasoning against reality. A confident hallucination passes its own P-Pass because the model does not know it is wrong. The methodology reduces errors caused by insufficient reasoning; it cannot fix errors caused by incorrect training data.

2. **The calibration problem.** Falsifiability conditions may themselves specify wrong thresholds. Domain expert review is required in safety-critical applications.

3. **Context window decay.** Directive adherence weakens over long sessions. Re-assertion at domain shifts mitigates this. It does not eliminate it.

4. **Model capability dependence.** On a frontier-class model, the P-Pass produces genuine adversarial analysis. On a weaker model, it produces the structure of adversarial analysis without its substance. Treat all outputs from less capable models as preliminary hypotheses requiring independent expert review. The formal model ([PAPER.md](PAPER.md), Section 2.1) quantifies this: when p ≈ 0, no number of passes produces corroboration.

5. **Domain boundary.** The methodology applies to STEM, engineering, and technical design. Applied to aesthetics, ethics, or pure preference, it produces false rigour. The suitability gate prevents this when correctly applied.

6. **No literature anchor.** The falsification process has no explicit test for consistency with published empirical literature. In high-stakes domains, an additional test should be added: does this claim contradict published experimental results?

7. **Single-practitioner validation.** This methodology has been developed and applied by one practitioner across multiple projects. The projects exist and function. Whether the methodology caused better outcomes than alternatives would have produced is not established. There is no counterfactual. The empirical validation framework (Part IX in [PAPER.md](PAPER.md)) exists to close this gap.

8. **Persistence dependency.** The version update mechanism and cumulative falsification require persistent memory to function across session boundaries. Without the persistence layer, the feedback loop resets at every session start. The methodology remains valid without persistence — each session applies the full P-Pass independently — but the cumulative knowledge that emerges from repeated falsification over time requires a memory architecture.

9. **Human operator dependency.** The manual constraint bounding described in Part III of the [white paper](PAPER.md) requires a human operator who understands the problem domain well enough to define effective boundaries. The methodology does not make a novice operator effective — it makes an already-competent operator more effective by providing a structured protocol for the AI side of the collaboration. The human skill is the prerequisite, not the output.

---

## Open Questions

Does methodology formalisation add value above a complexity threshold that correlates with constraint interaction density? Does multi-architecture review generalise beyond software to proof, design, and synthesis? Does schema competition produce measurably better methodologies? Is there a convergence limit for heterogeneous review beyond which adding architectures adds cost without coverage? Each is testable with existing infrastructure. See the [white paper](PAPER.md) Part XI for formal treatment.

---

## Worked Examples

Each of the following projects was built using this methodology. They are linked here as evidence of the methodology in practice, not as claims of superiority over alternative approaches. Each repo has its own documentation and stands independently.

| Project | What it is | Repo |
|---|---|---|
| **Project Genesis** | Trust-mediated labour market for mixed human-AI populations. Constitutional engineering, governance as falsifiable code, Popperian design methodology applied to social architecture. | [Project_Genesis](https://github.com/jebus197/Project_Genesis) |
| **Open Brain** | Persistent, cross-agent, cross-session verified memory for AI systems. The persistence and verification layer described in Part V of this document. | [OpenBrain](https://github.com/jebus197/OpenBrain) |

---

## Documentation

| Document | Audience | What it covers |
|---|---|---|
| [Extended Rationale](docs/EXTENDED_RATIONALE.md) | General | Why this methodology exists and what it means for AI-assisted STEM work |
| [White Paper](PAPER.md) | Technical | Formal methodology, mathematical models, empirical validation framework |
| [Founder's Notes](docs/FOUNDERS_NOTES.md) | General | Design intent, philosophical framing, falsification claims tested |
| [Mathematical Appendix](docs/MATHEMATICAL_APPENDIX.md) | Technical | Extensions to core models: residual risk, class-specific diversity, parameter uncertainty |
| [Domain Directives](bench/directives/README.md) | Practitioners | Domain-specific constraint boxes for the testbench |

---

## License

MIT. See [LICENSE](LICENSE).

---

Every claim in this methodology is presented as a falsifiable assertion. If any claim does not survive external testing, the methodology is improved by the correction. See the full [Invitation to Falsify](PAPER.md#invitation-to-falsify) in the paper.

*CDSFL v1.0. March 2026.*
