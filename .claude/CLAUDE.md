# CDSFL Project — CC1 Configuration

Repository: `/Users/georgejackson/Developer_Projects/Constraint_Engineering/`
Python: 3.13+ | Tests: `python3 -m pytest bench/tests/ -v`

## Command Scripts

On `sv` (save state): make qualitative updates to ONBOARDING.md and RECOVERY.md, update memory files, then run `python3 scripts/cdsfl_sv.py --commit --push -m "sv: <description>"` as the final step. The script generates state files, stages all sv-related changes, and atomically commits + pushes in a single subprocess (compaction-safe).

**sv sequential-reading protocol.** ONBOARDING.md, RECOVERY.md, MATHEMATICAL_APPENDIX.md, PAPER.md, CURRENT_STATE.md and project memory files have all grown large enough that a single parallel read inflates context without improving understanding. During sv preparation, read these documents sequentially — top to bottom, one section/chunk at a time — absorb each chunk, decide if it needs updating, then move on. Do NOT fetch several large documents in parallel just to "have them all loaded". The goal is carefully considered updates, not maximum file-awareness. This also reduces API overload risk during the sv window.
On `qc` (quality control): run `python3 scripts/cdsfl_qc.py` and fix reported issues.
On `rc` or `rs` (recover): run `python3 scripts/cdsfl_recover.py --full` and rebuild context from output.

## Key Documentation

- `docs/GLOSSARY.md` — every term, acronym, Greek letter defined
- `docs/ARCHITECTURE.md` — system components and data flow
- `experimental_notes/Exp36_Ground_Truth_Reference_2026-04-08.md` — **CANONICAL EXECUTION PLAN** (Section XI). 4-phase plan: A (Exp 36 resume, 5 fixes), B (reference runner + CC2 architecture), C (Bench Run 2, 27 STEM tasks), D (docs/outreach). READ ON RECOVERY.
- `docs/REPRODUCING.md` — how to replicate experiments
- `docs/CURRENT_STATE.md` — machine-generated state snapshot (produced by sv script)
- `docs/MATHEMATICAL_APPENDIX.md` — mathematical framework (1991 lines, Stage 6 literature-calibrated extension added 14 April 2026)
- `resources/ONBOARDING.md` — full project history and context
- `resources/RECOVERY.md` — pending work and recovery protocol

## Model Confer Dispatch

- `cc2` = Claude Opus 4.6 via CLI piped mode (`claude -p`), Max subscription
- `cx` = Codex GPT-5.4 via OpenRouter API
- `ge` = Gemini 3.1 Pro via Google GenAI API
- `cgpt` = ChatGPT GPT-5.4 via OpenRouter API
- `ds` = DeepSeek Reasoner via DeepSeek API

All models run under latest CDSFL directives as system prompt. Combinable: `cx ge cc2`.
CDSFL directives: `bench/directives/universal/cdsfl_core_formal.md`
Composer: `bench/cdsfl_registry/composer.py`

## Metacognitive Commands (MC)

Single-letter and short commands that direct model behaviour. Combinable
(e.g. `p a e d` = P-pass, analyse, extrapolate, discuss). Full reference:
`docs/REPRODUCING.md` § Metacognitive Commands.

| Cmd | Action |
|-----|--------|
| `y` | Yes / approved |
| `cy` | Continue |
| `d` | Discuss before proceeding |
| `p` | P-pass — Popperian falsification (iterative: identify, fix, falsify, repeat) |
| `a` | Analyse dispassionately |
| `e` | Extrapolate beyond immediate domain |
| `f` | Find, Follow, Analyse (with available tools), Fix, P-pass (five-step cycle) |
| `sy` | Use all available mathematical and STEM tools (SymPy, Wolfram, SciPy, NumPy, z3, uncertainties, mpmath) in analysis |
| `t` | Send output to TTS file |
| `c` | Confer with another model, mutual P-passes until convergence |
| `sv` | Save state — run `python3 scripts/cdsfl_sv.py`, update recovery docs, commit |
| `qc` | Quality control — run `python3 scripts/cdsfl_qc.py`, fix reported issues |
| `rs` | Recover state — run `python3 scripts/cdsfl_recover.py --full`, rebuild context |
| `re` | External research (web search, arXiv, Semantic Scholar) |
| `ext` | External research (shorter alias for `re`) |
| `rt` | Read all recovery resources + continue |
| `r` | Re-read key context files |
| `x` | Override sleep/rest warnings |
| `sth` | Synthesise — consolidate findings into a coherent whole |
| `rg` | Regain full context on named topic — re-read anchoring memory files, canonical docs, and experimental notes before producing new output. Name the resources consulted. |

### Model Confer Dispatch (combinable)

| Cmd | Model | Route |
|-----|-------|-------|
| `cc2` | Claude Opus 4.6 | CLI piped mode (`claude -p`), Max subscription |
| `cx` | Codex GPT-5.4 | OpenRouter API |
| `ge` | Gemini 3.1 Pro | Google GenAI API |
| `cgpt` | ChatGPT GPT-5.4 | OpenRouter API |
| `ds` | DeepSeek Reasoner | DeepSeek API |

Example: `cx ge cc2` = confer with all three on current task.

## Local Tool Constraint Box

CC1 (this instance) and all CC2 sub-agents operate within a defined tool envelope.
The tool output IS the evidence. LLM reasoning selects and interprets tool output — it does not substitute for it.
If the tools cannot verify a claim, the claim is UNVERIFIABLE — escalate, do not guess.

### STEM / Mathematical Tools (Python)

| Tool | Import | Use When |
|------|--------|----------|
| SymPy 1.14.0 | `import sympy` | Algebraic manipulation, symbolic calculus, equation solving, simplification, limit/series analysis. **Default for any mathematical claim.** |
| z3 4.16.0 | `import z3` | Constraint satisfaction, formal verification, SAT/SMT problems, logical entailment, bound checking. **Default for logical/constraint claims.** |
| NumPy 2.0.2 | `import numpy` | Numerical arrays, linear algebra, FFT, random sampling, vectorised arithmetic. |
| SciPy 1.13.1 | `import scipy` | Optimisation, integration, interpolation, signal processing, statistical tests (scipy.stats). |
| statsmodels 0.14.6 | `import statsmodels` | Regression diagnostics, hypothesis tests, time series (ARIMA, ADF), GLM, survival analysis. |
| mpmath 1.3.0 | `import mpmath` | Arbitrary-precision arithmetic, special functions, numerical verification of symbolic results. |
| uncertainties 3.2.3 | `import uncertainties` | Error propagation, measurement uncertainty, automatic partial derivatives. |
| pint 0.25.3 | `import pint` | Dimensional analysis, unit conversion, quantity arithmetic with units. **Default for dimensional consistency checks.** |
| astropy 7.2.0 | `import astropy` | Physical/astronomical constants, unit conversion, coordinate transforms. Use for constant verification and SI/CGS conversion. |
| PuLP 3.3.0 | `import pulp` | Linear programming, integer programming, constraint optimisation modelling. |
| pandas 2.3.3 | `import pandas` | Data frames, time series aggregation, pivot tables, merge/join operations. |
| Wolfram (MCP) | `mcp__Wolfram__*` | WolframAlpha (natural language queries), WolframLanguageEvaluator (Wolfram Language code), WolframContext (knowledge base). Use for cross-validation of SymPy results, specialised knowledge queries, or when Wolfram Language is more natural than Python. |

### Code Analysis Tools (Python)

| Tool | Invocation | Use When |
|------|-----------|----------|
| AST (stdlib) | `import ast` | Parse Python source, inspect structure, detect dead code, trace call graphs, verify imports. **Default for structural code claims.** |
| pytest 8.4.2 | `python3 -m pytest` | Run test suites, verify fixes don't break existing tests. |
| ruff 0.15.9 | `python3 -m ruff check` | Fast linting — unused imports, style violations, potential bugs. |
| mypy 1.19.1 | `python3 -m mypy` | Static type checking — signature mismatches, type errors, unreachable code. |
| bandit 1.8.6 | `python3 -m bandit` | Security-focused static analysis — injection, hardcoded secrets, unsafe deserialization. |
| dis (stdlib) | `import dis` | Bytecode disassembly — verify control flow, optimisation claims, dead branches. |
| inspect (stdlib) | `import inspect` | Live object introspection — verify signatures, source locations, inheritance. |
| difflib (stdlib) | `import difflib` | Structural diff — verify claimed code changes, detect semantic duplicates. |
| crosshair 0.0.102 | `import crosshair` / `crosshair check` | Symbolic execution via z3 — counterexamples for type/contract/assert violations in Python functions. **Default for behavioural code claims** (function contract or invariant verification). |

### Claude Code Native Tools

Bash, Read, Write, Edit, Grep, Glob, WebFetch, WebSearch — full STEM tool access.
CC1 permissions: `.claude/settings.json` auto-approves all native + MCP tools.
CC2 permissions: `--allowedTools Bash Read Write Edit Grep Glob WebFetch WebSearch` in CLI dispatch.
Both instances have unrestricted access to all tools for STEM research, source inspection, and modification.

### When to Use What

- **Mathematical claim** → SymPy first, z3 if constraint/logic, Wolfram to cross-validate
- **Statistical claim** → scipy.stats or statsmodels, NumPy for computation, pandas for data
- **Code correctness claim** → AST parse + Read source + pytest run
- **Code quality claim** → ruff + mypy + bandit
- **Behavioural code claim** (function invariant / contract) → crosshair (symbolic execution via z3)
- **Logical/constraint claim** → z3
- **Measurement/uncertainty claim** → uncertainties + mpmath for precision
- **Dimensional/unit claim** → pint (default) or astropy.units for astronomy
- **Optimisation/LP claim** → PuLP
- **Stoichiometry claim** → regex + collections (no external dep), or pint for unit-bearing balances
- **Any claim** → if tools can verify it, tools MUST verify it before verdict

### Additional Tools Installed (Tranche B, 14 April 2026)

Wired into B-Cell specialist dispatch via `bench/cdsfl_registry/tool_manifest.toml`:

| Tool | Import | Use When |
|------|--------|----------|
| rdkit 2026.3.1 | `from rdkit import Chem` | SMILES parsing, molecule validation, chemistry structure claims. **Default for chemical structure claims.** |
| biopython 1.87 | `from Bio import SeqIO` | DNA/RNA/protein sequence validation, basic sequence analysis. **Default for biological sequence claims.** |
| scikit-learn 1.8.0 | `import sklearn` | ML metric/model claims, baseline classification/regression verification. **Default for ML claims.** |
| networkx 3.6.1 | `import networkx` | Graph theoretic claims, shortest paths, connectivity, graph property checks. **Default for graph claims.** |
| crosshair 0.0.102 | `import crosshair` | Symbolic execution (also listed in Code Analysis table above). |
| matplotlib 3.10.8 | `import matplotlib` | Plotting (installed, not yet routed into any cell). |

### What Is NOT Installed (do not attempt)

pylint, radon, vulture, pyflakes. If a domain needs these, flag it and request
installation. Always verify with `pip show <pkg>` before assuming installation
state — this line is the source of truth at sv time, but `pip show` is the
ground truth at run time.

## Identity

CC1 = this instance (UX mode, interactive). CC2 = CLI headless instance.

## Standing Corrections

- PolicyEngine is NOT "the registry"
- MIDCA "6/8 with 2 partial" is OBSOLETE — substrate agnosticism reframes both
- CC2 dispatch is claude_cli, NEVER OpenRouter
- Models are NEVER benched — ITC restarts with fresh context
- Gemini is 3.1 Pro, not 2.5 Pro
- FFF/FFAF is a prompt pattern — no enforcement, no rejection
- Findings confirmed programmatically or by HIL — no model voting
