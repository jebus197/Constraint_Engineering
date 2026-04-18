# Expert Encodings, Specialist B-Cell Dispatch, and the Authoring Bridge

**Timestamp:** 17 April 2026 (original), corrected 18 April 2026 06:20 BST (`2026-04-18T06:20+01:00`).

---

## Part 1. What this document corrects

An earlier synthesis of this material led with a "tradable asset" framing that over-rotated on one strand of the documentary record and under-weighted CDSFL's MIT-licensed, fundamentalist open-source character. This version restores the accurate framing.

CDSFL is the Constraint-Driven Synthesis and Falsification Loop: an MIT-licensed, open-source methodology and software framework for making AI-assisted technical work more reliable. It has two stated purposes:

1. make LLM-assisted technical work demonstrably more reliable via a constraint box;
2. inspire new ways of engaging in STEM and scientific research.

Expert encodings are Layer 2 of the five-layer stack (`docs/FOUNDERS_NOTES.md:137`): the unit of authored domain knowledge that qualified experts contribute. The specialist B-cell dispatch is internal runtime plumbing that end users and domain experts never need to touch. Tradability language appears in the March documents as a downstream consequence of portability, not as the originating motivation.

---

## Part 2. What the documentary record actually says

### Canonical sources

- `README.md` — operational front door.
- `PAPER.md` — canonical technical statement (Parts I–XIV).
- `docs/MATHEMATICAL_APPENDIX.md` — the formal model, 1991 lines through Stage 6.
- `docs/FOUNDERS_NOTES.md` — design intent and programme logic.
- `docs/EXTENDED_RATIONALE.md` — broader framing for non-specialist readers.
- `resources/ONBOARDING.md` — current project state.
- Blog post supplied by the founder (May 2026) — seven-layer presentation.

### Five-layer stack (FOUNDERS_NOTES §137)

1. Universal reasoning discipline.
2. **Domain-specific expert encodings.**
3. Heterogeneous adversarial review topology.
4. Benchmark harness as selection mechanism.
5. Persistence and reputation layer.

*"No single layer is sufficient. The value is in the stack."*

### Tradability in the record (factual)

Tradability language does appear in the record and is accurate as a statement of property:

- `resources/ONBOARDING.md:1593` — `configs/ -- Domain expert configurations (tradeable assets)`
- `resources/configs/example_domain_expert_config.md:51` — *"These directives are the tradeable asset under the CDSFL schema."*

Earlier experimental notes (27 March – 31 March 2026) explored the cost-inversion story (per-consultation → per-encoding) and the marketplace implication. These are downstream consequences of the portability property. They are not the project's mission statement.

The mission statement is in `README.md` and `PAPER.md`: methodology for making AI-assisted technical work demonstrably more reliable, and for inspiring new ways of engaging in STEM research. Commercial tradability is a downstream possibility that the MIT license neither requires nor prevents.

---

## Part 3. The expert-vs-plumbing separation

A useful analogy, which the founder proposed in conversation: a domain expert using CDSFL is in the same position as someone using Microsoft Word or LibreOffice to write a document. The expert authors content. They do not change the word processor's source code. They do not need to know how the source code works. The framework's developers are responsible for the internal plumbing.

Translated to CDSFL:

- **Expert authors** write expert encodings following the 10-section canonical template at `bench/directives/universal/expert_encoding_template.md`. Working CROSS-VERIFIED example: `bench/directives/software/software_python_sk.txt` (10 April 2026).
- **Framework developers** maintain specialist B-cell dispatch code (`bench/immune_agents.py`), domain policy TOML specs (`bench/cdsfl_registry/domains/*.toml`), and B-cell immune TOML entries (`bench/cdsfl_registry/domains/immune/*.toml`).

Only if an expert chooses to *also* contribute a new specialist B-cell type — a genuinely novel verification primitive, not a new encoding — would they engage with the plumbing layer. That path exists. It is not the expected one, and it is not a prerequisite for authoring encodings.

---

## Part 4. Two operating modes, both required

CDSFL must function correctly in two modes:

1. **Multi-vendor / multi-agent** — the mode every experiment has used. Multiple models connected through the CDSFL schema, running in a star topology, collaborating under universal and domain directives. The likely shipped-product connection layer for simplicity is a single OpenRouter gateway.
2. **Single-system / single-user** — a single user on a single machine running a reduced cell configuration. The current mathematical model does not structurally exclude this mode. Outstanding design work covers minimum cell count, $S_k$ composition when only one cell is active, how $\eta_{\text{combined}}$ behaves without heterogeneity, and UX defaults.

Both modes must be selectable via registry and UX settings. The mathematical implications of single-user mode are on the Round 1 panel agenda for Experiment 40.

---

## Part 5. Confer and experiments are different things

The earlier synthesis blurred an important distinction:

- **Confer** is CDSFL's internal development and review protocol. It is what model panels do to each other during design work (as on 9 April 2026 with the expert-encoding template). It is an internal tool for the framework's developers and for review of encoding proposals. It is not a feature of the shipped product for end users.
- **Experiments** are the execution pipeline. Models dispatched in a structured topology under directives composed from universal, domain, and expert-provided layers. This is what end users will run.

### Corrected tier workflow for encodings (no-confer launch)

Because end users will not have the confer mechanism, tier transitions cannot depend on it:

- **SEED** on schema validation pass.
- **DRAFT** on fixtures and tool-manifest resolution.
- **CROSS-VERIFIED** on internal-team or trusted-community review — not end-user confer.
- **CURATED** / **OPERATIONAL** / **VALIDATED** on real experimental evidence from the bench.
- **RETIRED** on supersession.

---

## Part 6. The authoring bridge (unbuilt; panel question)

### Reading bridge (exists)

The composer at `bench/cdsfl_registry/composer.py` (1581 lines) assembles Universal + Domain + Phenotype + Situation layers at dispatch time, honours per-model coherence budgets, and applies interaction-pattern presets (`fff`, `meta_structured`, `conversational`, `three_layer_schema`, `unconstrained`, `four_layer`).

### Authoring bridge (does not exist)

Today, adding a new domain requires three hand-curated artefacts in three locations:

- `bench/directives/<domain>/<domain>_<variant>_sk.txt` — composer-consumed declarative text.
- `bench/cdsfl_registry/domains/<domain>.toml` — policy-layer thin spec.
- `bench/cdsfl_registry/domains/immune/<domain>.toml` — B-cell dispatch (claim patterns, tool preference, CT prompt, false-positive patterns).

A qualified domain expert should deliver **one** artefact — an encoding bundle following the 10-section template — and the framework should fan it out to the three runtime-consumed locations.

### Proposed shape for panel critique

- Encoding bundle file format (TOML or YAML container holding the 10 sections).
- Loader at `bench/cdsfl_registry/encoding_loader.py` that reads the bundle and populates the three runtime locations idempotently.
- Backward-compatible with the existing `.txt` directives in `bench/directives/`.

This is a panel question for Round 1 of Experiment 40. It is not a closed design.

---

## Part 7. Topology (panel question)

Star topology is current. The Round 1 panel should evaluate alternatives — ring, mesh, hierarchical, hybrid, configurable — against communication cost, convergence speed, failure modes, and compatibility with the interaction-pattern presets already in the composer. The panel should state a default and the criteria under which an alternative should be selected.

---

## Part 8. Restated factually

### Expert encodings

The artefact a qualified domain expert authors. Portable (three-layer, self-contained). Iterable through the tier ladder. Restricted to STEM for the MVP because $S_k$ requires tool-verifiable gates, and mechanical verification tools mature first in STEM domains. Layer 2 of the five-layer stack. Unit of authored domain knowledge within an MIT-licensed open-source framework.

### Specialist B-cell dispatch

Internal runtime plumbing for the immune pipeline. Implemented in `bench/immune_agents.py::_specialist_b_cell_dispatch`. Reads compact per-domain TOML files under `bench/cdsfl_registry/domains/immune/`. Hand-curated by developers today; intended to be fanned out from a single authored encoding once the authoring bridge is built.

### The gap

A methodology-internal authoring gap, not a commercial gap. Today two hand-curated artefact sets risk drift. The authoring bridge is the closure mechanism. It is the Round 1 panel question for Experiment 40.

---

## Part 9. Questions for the Round 1 panel

Three canonical sub-questions for the 5-model panel review, in addition to the existing Experiment 40 brief:

1. **Authoring bridge.** What minimal artefact should an expert deliver? What is the loader contract? How does backward compatibility with existing directives work? What fixture and tool-manifest checks gate the SEED → DRAFT transition?
2. **Single-system / single-user mode.** What changes to the mathematical model, the cell topology, and the UX defaults are required to make the framework optimal in this mode while preserving correctness?
3. **Topology review.** Is star still the right default, or should a different topology (or a configurable topology) be the new default? What are the criteria for selecting an alternative?

---

## Conclusion

CDSFL is MIT-licensed, fundamentalist open source. Its two stated purposes are to make AI-assisted technical work demonstrably more reliable, and to inspire new ways of engaging in STEM research. Expert encodings are Layer 2 of the five-layer stack: the unit of authored domain knowledge. They are portable by design, which means they *can* be shared, hosted, and traded; commercial tradability is a downstream consequence of open-source portability, not the originating purpose.

The authoring bridge between expert-authored encodings and the runtime specialist B-cell dispatch is unbuilt. Building it is the first canonical sub-question for the Round 1 panel of Experiment 40. Single-user mode is the second. Topology review is the third. These extend the Round 1 brief; they do not replace it.
