# Cell Type Architecture for CDSFL Domain Generalisation — 9 April 2026

## Core Insight

The CDSFL framework generalises not by becoming general-purpose, but by **hosting specialist components that share a common protocol** — exactly as in biology.

## Biological Mapping

| Biology | CDSFL |
|---------|-------|
| Organism | Framework (runner, brain, immune, endocrine, registry) |
| Cell types | Domain-specific verification modules (Python cells, maths cells, chemistry cells) |
| Circulatory system | Finding registry + message passing |
| Immune system | Quality filtering — domain-agnostic, operates on quality signals from any cell type |
| Brain | Convergence tracking — $\gamma/\rho$ from any finding stream |
| Endocrine | Health diagnostics — runs whatever checks active cell types define |

## What Each Cell Type Provides

```
cell_type:
  domain: "python_code"
  tool_mappings: [ast, pytest, ruff, mypy, bandit, sympy, z3]
  hard_gates: [g1_parse, g2_compile, g3_type_check]
  effect_evidence: [e1_targeted_test, e2_regression, e3_lint, e4_security, e5_symbolic]
  fix_format: "SEARCH/REPLACE blocks"
  flaw_taxonomy: [correctness, security, design, robustness, performance, documentation]
  health_checks: [pyright_diagnostics, ruff_violations, test_coverage]
```

## Multi-Cell $S_k$ Composition

When multiple cell types are active (e.g., software + mathematics for a SymPy module):

$$A = \prod_{\text{all active cell types}} \prod_{j \in \mathcal{G}_{\text{hard}}} g_j$$

$$E = \text{aggregate}\Big(\{e_m^{w_m}\}_{\text{all active cell types}}\Big)$$

$$S_k = A \cdot E$$

Hard gate veto works **across** cell types. A code fix that parses ($g_{s1}=1$) but implements a dimensionally inconsistent equation ($g_{m1}=0$) gets $S_k = 0$.

The mathematical model **does not change**. It receives more gates when more cell types are active.

## Activation Routing

**Hybrid approach (most robust):**

1. **Explicit**: Task specification declares primary domain → activates corresponding cell types
2. **Implicit**: Content analysis detects secondary domains (e.g., SymPy imports → activate maths cells)
3. **Immune system**: Doesn't need to know which cell type produced a finding — evaluates quality signals regardless

Adding a new domain = write an expert encoding + register with composer. Runner, immune, brain, endocrine all work unchanged.

## Cross-Domain Composition

Current monolithic cross-domain directives (`cross_software_hardware.txt`, etc.) become natural compositions:

- Activate relevant cell types from each domain
- Each contributes findings independently
- Each contributes verification gates to $S_k$
- Cross-domain directive defines the **interface** between cell types, not a separate encoding

## P-Pass Results (5 passes, all survived)

| Pass | Challenge | Outcome |
|------|-----------|---------|
| 1 | Multi-cell $S_k$ composition sound? | **Survives** — $A \cdot E$ structure handles naturally |
| 2 | Activation routing robust? | **Survives** — hybrid explicit + implicit |
| 3 | Cross-domain cleaner? | **Survives** — composition > monolithic encoding |
| 4 | Combinatorial explosion? | **Survives** — only relevant cells activate per task |
| 5 | Where does it break? | **Survives with boundary** — zero-gate domains → ESCALATE to HIL |

## Extrapolation

1. **CDSFL becomes a meta-framework.** It provides infrastructure for domain-specific agents to collaborate under structured falsification. The generality is in the protocol, not in the specialists.

2. **Cell types evolve through self-improvement.** When the panel discovers a missing verification gate, that discovery is a finding about the cell type itself. The system improves its own specialist components. (Ouroboros at the architectural level.)

3. **Adaptive activation.** Historical $\gamma/\rho$ data could predict which cell types will be most productive for a given task. [SPECULATIVE — requires empirical validation from BR2 data.]

## Tooling Maturity (NOT Schema Limitations)

The schema is **complete**. The tooling ecosystem is what may be incomplete.

1. **Domains with partial tool coverage**: ESCALATE is a **development signal**, not a boundary. Domain experts build the missing tools for integration into the schema. Within STEM, every claim is in principle verifiable — there is no domain where verification tools are theoretically impossible. Absence of evidence is not evidence of absence.
2. **Cross-cell communication**: Current architecture assumes independent evaluation. If finding correctness depends on another cell type's result, shared state would be needed. Independent evaluation sufficient for BR2. Cross-cell communication is a future capability, not a schema gap.
