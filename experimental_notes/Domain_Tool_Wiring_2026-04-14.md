# Domain Tool Wiring

**Date:** 14 April 2026, session complete 18:37 BST
**Branch:** `exp39-experimental`
**Scope:** B-Cell specialist dispatch — 9 new wrappers, 5 TOML updates, full regression green

---

## Context

The CDSFL immune pipeline's specialist B-Cell dispatch stage routes domain-specific claims to domain-specific verification tools. Prior to this session, the dispatch handled only SymPy, z3, statsmodels and SciPy. Fourteen further tools had been installed on the host but were not wired. The task was to write subprocess wrappers for each installed tool and register them in the dispatch, so non-coding STEM domains (physics, chemistry, biology, engineering) could verify claims mechanically rather than relying on SymPy alone.

## Tool inventory

Thirteen of the fourteen tools are installed and reachable. Crosshair is the exception. Pint is installed, despite a stale `NOT installed` note in the global `CLAUDE.md`; direct `import pint` succeeds, so the global note has been superseded.

| Tool | Install status | Role |
|------|----------------|------|
| pint | installed | dimensional analysis |
| uncertainties | installed | error propagation |
| pulp | installed | linear programming |
| astropy | installed | physical constants, unit conversion |
| hypothesis | installed | property-based testing (not yet wired) |
| beartype | installed | runtime type checking (not yet wired) |
| icontract | installed | design-by-contract (not yet wired) |
| crosshair | **NOT installed** | symbolic execution |
| mypy | installed | static type checking |
| pyright | installed | alt type checker (not yet wired) |
| ruff | installed | linting |
| bandit | installed | security scanning |
| mutmut | installed | mutation testing (not yet wired) |
| coverage | installed | code coverage (not yet wired) |

## What was added

Nine new wrapper functions were added to `bench/immune_agents.py`. Each takes a claim string (and, for code tools, a target file path), invokes a tool in a subprocess, parses structured output tokens, and returns a `CellVerdict` with `verdict`, `confidence`, `evidence`, and `tool_used`.

### STEM wrappers (claim-only)

| Wrapper | Tool | Verdict tokens |
|---------|------|----------------|
| `_verify_dimensional_analysis` | pint | `DIM_CONSISTENT` / `DIM_INCONSISTENT` |
| `_verify_uncertainty_propagation` | uncertainties | `UNC_CONSISTENT` / `UNC_INCONSISTENT` |
| `_verify_stoichiometric_balance` | regex + collections | `STOICH_BALANCED` / `STOICH_UNBALANCED` |
| `_verify_linear_programming` | pulp | `LP_PARSED` / `LP_BOUND_ONLY` |
| `_verify_astronomical` | astropy | `ASTRO_VERIFIED` / `ASTRO_MISMATCH` |

### Code wrappers (claim + file_path)

| Wrapper | Tool | Verdict tokens |
|---------|------|----------------|
| `_verify_type_check` | mypy | `TYPE_CLEAN` / `TYPE_ERROR` |
| `_verify_lint_check` | ruff | `LINT_CLEAN` / `LINT_VIOLATION` |
| `_verify_security_scan` | bandit | `SEC_CLEAN` / `SEC_ISSUE` |
| `_verify_bytecode_analysis` | dis | `BYTE_CLEAN` / `BYTE_DEAD_CODE` |

## Dispatch changes

`_specialist_b_cell_dispatch()` was extended with nine new `elif` branches (lines 1912–1929 of `immune_agents.py`). For code-domain tools, the dispatch reads `tf.finding.target_file` and passes it to the wrapper. For STEM tools, only the claim string is passed. The first-definitive-result-wins semantics is preserved.

## Domain configuration updates

Five TOML configuration files were updated to reference the new tools:

| File | Added to mathematical | Added to statistical |
|------|----------------------|----------------------|
| `physics.toml` | `astronomical` | `uncertainty_propagation` |
| `engineering.toml` | `linear_programming` | `uncertainty_propagation` |
| `chemistry.toml` | `dimensional_analysis` | `uncertainty_propagation` |
| `biology.toml` | `dimensional_analysis` | `uncertainty_propagation` |
| `cross_domain.toml` | `dimensional_analysis` | `uncertainty_propagation` |

`cs_software.toml` was already referencing `type_checker`, `lint_check`, `security_scan`, and `bytecode_analysis` from a prior session, so only dispatch wiring was needed on the code side.

## Verification performed

| Check | Result |
|-------|--------|
| Syntactic parse (`ast.parse`) | OK |
| 9 wrapper definitions present | 1114–1734 |
| 9 dispatch branches present | 1912–1929 |
| `pytest --collect-only` | 793 tests (unchanged) |
| Immune-scoped tests (`-k "immune or b_cell or specialist or dispatch"`) | 136 passed, 657 deselected, 4m 44s |
| Individual wrapper smoke tests | 9/9 return expected verdicts |
| Full regression suite | 793 passed in 17m 21s |

## Bugs found and fixed during smoke testing

Two bugs were found and fixed before the full regression run.

**Bug 1 — dimensional analysis regex.** The quantity extraction regex required units to be 2+ characters, so single-letter units (`m`, `s`, `N`, `K`) were silently skipped. The unit character class was relaxed from `[a-zA-Z0-9_/^*]+` to `[a-zA-Z0-9_/^*]*`, making the overall pattern require 1+ chars starting with a letter. `immune_agents.py:1131`.

**Bug 2 — ruff output-format argument.** Ruff rejected `--output-format=text`. The valid values begin with `concise`. The argument was corrected. `immune_agents.py:1626`.

After both fixes, all nine wrappers produced the expected verdicts on their trivial test inputs, and the full regression suite remained green.

## Shadow status

The new wrappers run inside `_specialist_b_cell_dispatch()`, which itself runs in shadow mode in experiment 39. The specialist verdicts are captured and logged (via `specialist_verdicts` at the call site) but do not yet count towards the final verdict tally. Promotion to active is a single-line change at `bench/reference_runner.py` line ~3741 — specifically switching the shadow logging to `all_verdicts.extend(specialist_verdicts)`. No structural changes to the dispatch or wrappers are needed for promotion.

## Installation gap recorded

- **crosshair** — not installed. If a future domain requires symbolic execution, install first.
- **hypothesis, beartype, icontract, pyright, mutmut, coverage** — installed but not wired into any cell. Whether these should be wired depends on cell design (not in scope for this session).

## Hygiene notes

The session included an Anthropic API 500 part way through. The error was triggered mid-session during a single `Edit` call inserting all nine wrappers (~580 lines) in one payload. The post-mortem (`bench/API_500_SELF_DIAGNOSIS.md`) identified edit size, parallel tool batching, and large grep outputs as contributing factors. After the error, work resumed with: one edit per tool call, targeted grep patterns, single-claim smoke tests. The bug-fix cycle was done as discrete Read → Edit pairs, not batched.

## Closing

The specialist B-Cell dispatch now routes to thirteen verification tools across mathematics, physics, chemistry, biology, engineering, and code domains. The dispatch is exercised by existing unit tests and confirmed clean through the full regression. Changes preserve first-definitive-result-wins semantics, the shadow-mode guarantee, and the confidence scoring contract. No final verdicts change in experiment 39 until the shadow flag is flipped at `reference_runner.py`.

## Artefacts

- Modified: `bench/immune_agents.py` (+9 wrappers, +9 dispatch branches, 2 bug fixes)
- Modified: `bench/cdsfl_registry/domains/immune/physics.toml`
- Modified: `bench/cdsfl_registry/domains/immune/engineering.toml`
- Modified: `bench/cdsfl_registry/domains/immune/chemistry.toml`
- Modified: `bench/cdsfl_registry/domains/immune/biology.toml`
- Modified: `bench/cdsfl_registry/domains/immune/cross_domain.toml`
- TTS: `~/Desktop/CDSFL_tts/Domain_Tool_Wiring_2026-04-14.txt`
- Note: this file
