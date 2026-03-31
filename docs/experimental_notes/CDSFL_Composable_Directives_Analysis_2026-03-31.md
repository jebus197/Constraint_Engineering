# Composable Directive Architecture for CDSFL

**31 March 2026 — P-Pass, Analysis, and Extrapolation**

## The Claim

CDSFL directives can be decomposed into modular, composable packets that combine dynamically per-dispatch to create task-specific cognitive configurations. This preserves core Popperian constraints while tightening the problem space. Evidence suggests this produces genuine cognitive diversity more efficiently than multiple frontier models.

## Evidence Chain

1. CX (same weights + different config) ≠ ChatGPT (same weights + bare config) — **demonstrated**
2. Therefore configuration drives at least some cognitive diversity — **demonstrated**
3. Therefore modular, composable configurations could manufacture diversity — **plausible, not yet tested**
4. Therefore dynamic per-dispatch composition is the natural architecture — **logically follows**
5. Therefore the configured synthetic domain expert is buildable today — **yes, pieces exist**

## P-Pass Results (5 passes)

### Pass 1: Combinatorial contradiction risk
If N directive packets combine in 2^N ways, arbitrary compositions could create contradictions ("be conservative" + "be adversarial" = oscillation). **Result:** Real risk, already solved. The `cdsfl_registry` uses monotonicity enforcement — lower layers cannot weaken HARD constraints from higher layers. `PolicyViolationError` fires at merge time. Same mechanism extends to dynamic composition. **Risk: manageable.**

### Pass 2: This already partially exists
`cdsfl_registry/` has `universal.toml` + 28 domain files. `configs/` has portable expert configs. **Result:** What exists is **static** composition (TOML selected at benchmark start). What's proposed is **dynamic** composition (assembled per-dispatch based on task/model/round/performance). That IS genuinely new. **Claim holds — extends, doesn't duplicate.**

### Pass 3: Coherence under dynamic assembly
Monolithic directives guarantee consistency (human-authored unit). Dynamic packets might produce incoherent instruction sets. **Result:** Real risk, but testable. The confer packet already demonstrates composed prompts outperforming monolithic ones. **Risk: real but empirically testable.**

### Pass 4: The packet analogy
Network packets are stateless/order-independent. Directive packets may have dependencies. **Result:** Better analogy: **microservices for cognition** — small, composable, independently testable cognitive modules with well-defined contracts. **Principle survives.**

### Pass 5: Does config diversity produce independent findings?
CX ≠ ChatGPT despite same weights, but N=1 for configuration-driven diversity. **Result:** Key falsifiable prediction needs more data. [SPECULATIVE] Different directive compositions producing different analytical phenotypes is plausible but not yet validated. **Design the experiment.**

## The Four-Layer Directive Stack

| Layer | Scope | Changes When | Example | Status |
|---|---|---|---|---|
| **Universal** | All tasks, all models | Never | falsification_required, anti_deference, HARD/SOFT | ✅ Exists |
| **Domain** | Per problem domain | Domain changes | Structural safety, medical protocols | ✅ Exists (28 files, 10 domains) |
| **Phenotype** | Per model/class | Capability observed | CX: tighter box; DeepSeek: simpler prompts | ⚠️ Partial (Layer 4, not wired) |
| **Situation** | Per dispatch | Every dispatch | Verified facts, code, adversarial brief | ✅ Exists (confer packet) |

**Missing piece:** Dynamic composer (~200-400 lines) that assembles all four layers per-dispatch.

## The Compartmentalised Thinking Parallel

Humans don't load their entire knowledge base for every problem. They activate relevant schemas, constrain the search space, iterate within bounds. Composed directives achieve the same for LLMs: activate relevant modules, constrain to the problem at hand, iterate under Popperian falsification within those bounds.

The TCP/IP analogy: each layer has a clear contract with layers above and below. IP doesn't care about application semantics. TCP doesn't care about routing. Similarly: universal layer doesn't care about domain specifics. Domain layer doesn't care about model phenotype. Each layer adds constraint without understanding the layers above.

## Extrapolation

### What generalises

1. **Expert bottleneck inverts.** Building a domain expert shifts from training (expensive, slow, needs data) to directive composition (cheap, fast, needs domain knowledge). Scarce resource: domain encoding skill, not compute.

2. **Diversity becomes tuneable.** Manufacture cognitive diversity via configuration: risk-averse, adversarial, precision-focused, exploratory — each a validated directive module, not a different model.

3. **Tradable engineered artefact.** Modular, composable, validated, portable expert configurations become intellectual property. Value migrates from "biggest model" to "best expert encodings."

4. **Genesis connection.** The configured synthetic domain expert IS the machine actor in Genesis's labour market. Competence from composition, not training. Performance measurable. Expertise tradable.

### Boundary conditions

- Breaks if composition produces confusion > diversity (testable)
- Quality ceiling partially set by base model (weak model + perfect directives still has limits)
- Breaks if composition space too small for meaningful diversity (measurable)

### Falsifiable questions

1. Does N compositions of one model ≈ diversity of N different models?
2. Minimum effective composition size?
3. Composed vs monolithic directives of equal length?
4. Does composition order matter?
5. Can the composition engine itself be automated? (Meta-composition)

## Buildable Today

The dynamic composer is ~200-400 lines of Python. Reads task context → selects domain + phenotype packets → assembles with universal + situation → validates monotonicity → emits per-dispatch directive set.

Core Popperian mechanics don't change. Falsification remains the engine. What changes: how efficiently the search space is constrained *before* falsification begins. The method isn't abandoned — its application becomes more precise.

**Proposed: Experiment 19 — "Does dynamic directive composition produce equivalent finding quality at lower token cost?"**
