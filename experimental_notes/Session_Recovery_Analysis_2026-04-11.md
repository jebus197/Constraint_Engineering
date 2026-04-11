# Session Recovery Analysis — 11 April 2026

## What Was Built Without Authorisation

The previous CC1 session received `r c` (read + confer) and `x` (override rest). What was delivered went substantially beyond that scope.

**The real problem:** Exp 38 R0 DC v2 classifier misrouted 17/26 code findings to MATHEMATICAL (operators like `>=`, `==`, `=` in code descriptions). 3/26 defaulted to UNCATEGORISED (no cell processes these).

**What was built (not authorised):** A complete 3-layer classification architecture in `bench/immune_agents.py` — 398 lines changed:

- **Layer 1:** `_CODE_CONTEXT_PATTERN` (12 Python-construct branches), checked before math. `_STRONG_MATH_SIGNAL` (18 terms) vetoes code-context override for genuine math.
- **Layer 2:** Targeted LLM classifier for UNCATEGORISED residue (15s timeout, fail-open, confidence 0.55).
- **Layer 3:** Domain TOML loading + hard verification gate (nothing exits without CT/B-Cell/NK verdict).
- **Two CX confers** (only one arguably within `r c` scope). CX-F1: removed bare-word branches. CX-F2: added 6 strong-math terms.
- **24 new tests**, 1 currently failing.

## The Timeout Problem

Layer 2 LLM classifier has a 15-second timeout. This contradicts the current objective: **end-to-end completion generating concrete results in all cases**, not speed optimisation. A short timeout that triggers fail-open silently loses classification data.

## The Reference Runner Question

| File | Status | Proven? |
|------|--------|---------|
| `run_exp37_evidence.py` | Untouched since `944ec3e` | **YES** — converged at R15, 222 canonical, γ=0.467 |
| `reference_runner.py` | Created post-Exp 37 in `9d2ac85`, 99 lines uncommitted changes | **NO** — never run to convergence |

`reference_runner.py` was a parameterised extraction from `run_exp36_evidence.py`, created during Exp 37 forensic analysis. It has never proven itself. The 14 ouroboros bug fixes were applied to this unproven runner, not to the proven one.

## Working Tree State

**Clean (untouched since Exp 37):**
- `run_exp37_evidence.py` — the runner that converged
- `runner_core.py` — shared infrastructure

**Modified (uncommitted):**
- `bench/reference_runner.py` — 99 lines, 14 bug fixes (applied to wrong runner)
- `bench/immune_agents.py` — 398 lines, 3-layer classification (not authorised)
- `bench/endocrine.py` — 53 lines, SEARCH/REPLACE parser + target fallback (needed for CC2)
- `bench/insect_brain.py` — 1 line, domain wiring

## Path Forward Options

**Option A:** Revert all. Start fresh from `run_exp37_evidence.py` as true reference. Apply fixes one at a time with discussion.

**Option B:** Keep endocrine fixes (clearly needed). Revert immune classification changes, discuss approach before reimplementing. Verify 14 runner bugs exist in `run_exp37_evidence.py` before applying.

**Option C:** Keep everything, but `run_exp37_evidence.py` remains the reference. `reference_runner.py` is an experimental fork needing proof.

**Assessment:** Option B. Endocrine fixes are defensive. Immune classification problem is real but 3-layer solution was over-engineered without discussion. Runner bugs need verification against the proven runner. LLM classifier timeout needs to be generous or removed.
