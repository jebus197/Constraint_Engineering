# STEM Verification Tool Audit for CDSFL Pipeline

**Date:** 2026-04-05

## 1. Installation Status

All tools checked against Python 3.13 framework (`/Library/Frameworks/Python.framework/Versions/3.13/bin/`) and `pip3 list`.

### Installed (18 tools)

| Package | Version | Binary | Category |
|---------|---------|--------|----------|
| sympy | 1.14.0 | `isympy` | Symbolic maths |
| z3-solver | 4.16.0.0 | `z3` | SMT solver |
| numpy | 2.0.2 | — | Numerical computing |
| scipy | 1.13.1 | — | Scientific computing |
| hypothesis | 6.151.9 | `hypothesis` | Property-based testing |
| beartype | 0.22.9 | — | Runtime type checking |
| icontract | 2.7.3 | — | Design-by-contract |
| crosshair-tool | 0.0.102 | `crosshair` | Symbolic execution |
| pint | 0.25.3 | `pint-convert` | Units / dimensional analysis |
| uncertainties | 3.2.3 | — | Error propagation |
| mypy | 1.20.0 | `mypy`, `dmypy`, `mypyc` | Static type checking |
| pyright | 1.1.408 | `pyright` | Static type checking |
| ruff | 0.15.9 | `ruff` | Linter / formatter |
| bandit | 1.9.4 | `bandit` | Security linter |
| mutmut | 3.5.0 | `mutmut` | Mutation testing |
| coverage | 7.13.5 | `coverage` | Code coverage |
| PuLP | 3.3.0 | `pulptest` | Linear programming |
| astropy | 7.2.0 | various | Astrophysics |

## 2. Pipeline Integration Status

Searched all `.py` files under `bench/` (excluding logs/transcripts).

### Integrated (actively used in pipeline code)

| Tool | Where Used | How |
|------|-----------|-----|
| **sympy** | `immune_agents.py`, `verification_utils.py`, `interactive_smoke.py` | B-cell verification layer; `verify_sympy()` with AST blocklist security |
| **z3-solver** | `immune_agents.py`, `verification_utils.py` | Logical invariant verification; `verify_z3()` for numeric + if-then logic |
| **numpy** | `dm/_types.py`, `dm/_load_balancer.py`, `dm/_role_assignment.py`, `dm/_convergence.py`, `dm/_diminishing_returns.py`, `dm/_failure_handler.py`, `dm/_immune.py`, `decay_analysis.py`, tests | Core numerical engine for dynamic management subsystem |
| **scipy** | `decay_analysis.py` | `curve_fit`, `gammaln` for decay curve analysis |
| **ast** (stdlib) | `verification_utils.py` | Structural code verification via `verify_ast_claim()` |
| **regex stats** | `verification_utils.py` | `verify_statistical()` — regex extraction of p-values/correlations (no actual statsmodels) |

### NOT Integrated (14 tools installed but unused)

**Category A — Code Quality (not used for bench code):**
- hypothesis, beartype, icontract, crosshair-tool
- mypy, pyright, ruff, bandit, mutmut, coverage

**Category B — STEM Verification (not used for claim checking):**
- pint, uncertainties, PuLP, astropy

### Configuration Gap

- No `pyproject.toml` found
- No `.pre-commit-config.yaml` found
- No `Makefile` found
- `requirements.txt` lists only: `anthropic`, `openai`, `scipy`

## 3. Gap Analysis: STEM Correctness Engine Beyond Software

The current pipeline verifies: symbolic maths (sympy), logical constraints (z3), statistical claims (regex parsing). For a general-purpose STEM correctness engine:

### Physical / Engineering Verification

| Need | Tool Status | Notes |
|------|-------------|-------|
| Dimensional analysis / unit consistency | **pint installed, unused** | Can verify equation dimensional consistency |
| Conservation law checking | Not installed | Would require physics-aware constraint sets on z3/sympy |
| Tolerance / uncertainty propagation | **uncertainties installed, unused** | Critical for engineering claims with measurements |

### Statistical Verification

| Need | Tool Status | Notes |
|------|-------------|-------|
| Recompute claimed statistics | Not integrated | `verify_statistical()` only regex-parses, doesn't compute |
| Power analysis | Partial (scipy.stats available) | `statsmodels.stats.power` not installed |
| Effect size / CI checking | Not integrated | — |
| Multiple comparison correction | Not integrated | — |

### Logical / Formal Verification

| Need | Tool Status | Notes |
|------|-------------|-------|
| Deeper z3 usage | Partially integrated | Currently handles only numeric comparisons + simple if-then |
| Proof assistants (Lean/Coq) | Not installed | High barrier to integration |
| Model checking | Not installed | Candidates: `pynusmv` |

### Numerical Verification

| Need | Tool Status | Notes |
|------|-------------|-------|
| Arbitrary precision | mpmath installed (sympy dep), unused directly | — |
| Numerical stability | Not integrated | `numpy.linalg.cond` available |
| Interval arithmetic | Not installed | Candidates: `mpmath.iv`, `python-flint` |

### Domain-Specific (not installed)

| Domain | Packages |
|--------|----------|
| Chemistry | RDKit, OpenBabel, pymatgen, ASE |
| Biology | Biopython, scikit-bio |
| Electrical engineering | PySpice, lcapy |
| Mechanical / civil | OpenMDAO, FEniCS |
| Control systems | python-control |
| Thermodynamics | CoolProp, Cantera |
| Geoscience | ObsPy, MetPy |

## 4. Priority Recommendations

### Immediate (installed, low effort)

1. **pint** — dimensional analysis of physics/engineering claims
2. **uncertainties** — error propagation verification
3. **ruff** — linting config for bench code quality
4. **pyproject.toml** — centralise config and declare actual dependencies

### Medium-term (moderate effort)

5. **hypothesis** — property-based testing of immune pipeline, load balancer, convergence detector
6. **coverage + mutmut** — measure and improve test suite effectiveness
7. **scipy.stats** — replace regex-based statistical "verification" with actual computation
8. **mypy/pyright** — type checking (annotations already present in codebase)

### Longer-term (general STEM engine)

9. **crosshair + icontract + beartype** — contract-based verification stack
10. **Domain-specific packages** — chosen based on target STEM domains
