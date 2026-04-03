# Run 9 Analysis

**Date:** 3 April 2026
**Duration:** 120 minutes (20 rounds)
**Findings:** 425 total, 65 unique finding IDs
**Termination:** MAX_ROUNDS (no convergence detected)

## Key Metrics — Run 8 vs Run 9

| Metric | Run 8 | Run 9 | Change |
|--------|-------|-------|--------|
| Total findings | 339 | 425 | +25% |
| Unique finding IDs | 30 | 65 | +117% |
| Churn rate | 91.2% | 84.5% | −6.7pp |
| γ (Duane raw) | −0.041 | +0.157 | Flipped sign |
| C(H,E) Popper | 0.789 | 0.828 | +0.039 |
| Elapsed | 52 min | 120 min | 2.3× |
| Task packet | 3.8K shim | 244K real | 65× |
| Models with impl findings | CC2 only | All 5 | Task packet fix |
| Immune verdicts | 100% UNCERTAIN | 95% UNC, 5% DUP | Pipeline active |

## Per-Round Finding Counts

```
[34, 29, 26, 21, 29, 21, 24, 22, 19, 16, 21, 17, 17, 16, 22, 19, 17, 18, 19, 18]
```

## Per-Model Totals

- **CC2:** 129 findings
- **ChatGPT:** 118 findings
- **Codex:** 97 findings
- **DeepSeek:** 54 findings
- **Gemini:** 27 findings (benched at R5)

## Three Infrastructure Bugs

### Bug 1: `continue` Bypass (Critical)

**Location:** `run_baseline_confer.py`, line 1399

When the DM FSM went terminal at Round 5, the exception handler's `continue` statement skipped the γ-on-clusters convergence check (line 1430). The convergence detection built and calibrated from Run 8 data ran for exactly 3 rounds (R2, R3, R4), then was never called again.

γ_novel trajectory (rounds 2–4 only):
- R2: γ_novel=0.355, novel_per_round=[32, 20, 13]
- R3: γ_novel=0.348, novel_per_round=[32, 20, 13, 14]
- R4: γ_novel=0.324, novel_per_round=[32, 20, 13, 14, 16]

**Fix:** Move convergence check outside try/except block or into `finally`.

### Bug 2: Hardcoded `tau_sim=0.8` (Critical)

**Location:** `run_baseline_confer.py`, line 1209

The runner explicitly passes `tau_sim=0.8` to `run_immune_pipeline()`, overriding the calibrated default of 0.33 in `_types.py`. The NK Cell's similarity dedup threshold was unreachable — same problem as Run 8.

Result: 21 duplicates caught out of ~355 restatements (6% detection rate).

**Fix:** Remove explicit `tau_sim=0.8` kwarg.

### Bug 3: DM FSM Terminal Failure

**Location:** DynamicManager FSM

The FSM entered `TerminationReason.FAILURE` at Round 5 and never recovered. All subsequent rounds ran without DM feedback. Immune dispatch recommendations (EXCLUDE, ABORT) flowed through the no-exclusion override only.

**Fix:** Investigate FSM state machine — why does EXCLUDE cascade into unrecoverable FAILURE?

## Immune Pipeline Detail

| Round | Findings | Tools (CT/NK/FP/AD) | Verdicts | Rejection |
|-------|----------|---------------------|----------|-----------|
| R0 | 34 | 3/0/0/0 | 34 UNC | 0% |
| R1 | 29 | 2/0/0/0 | 29 UNC | 0% |
| R6 | 24 | 6/1/0/1 | 23 UNC, 1 DUP | 4% |
| R12 | 17 | 10/9/0/0 | 8 UNC, 9 DUP | 53% |
| R14 | 22 | 5/5/0/0 | 17 UNC, 5 DUP | 23% |
| R15 | 19 | 7/4/0/0 | 15 UNC, 4 DUP | 21% |
| R18 | 19 | 2/2/0/0 | 17 UNC, 2 DUP | 11% |

**B-Cell:** 0 usage across all 20 rounds (SymPy/z3 verification path not firing).
**CT:** Fires in 14/20 rounds but returns UNCERTAIN on everything except near-exact duplicates.

### Post-Run Root Cause Analysis (Bugs 4–6)

**Bug 4: B-Cell f-string escape (Critical — Silent Cell Death)**
`_verify_z3()` line 752: `{len(nums)}` inside an f-string code template was
interpolated by the *outer* Python process instead of being passed through to
the subprocess. NameError crashed b_cell_verify(), caught by silent
`except: pass` at line 1248. Same bug in `_verify_statistical()` lines 795–808.
Result: entire B-Cell pipeline dead for all runs since immune layer was added.

**Bug 5: Silent exception swallowing (Critical)**
Pipeline exception handler (line 1246–1248) used bare `pass`, hiding Bug 4.
Any cell crash was invisible. Fixed with `logging.warning()`.

**Bug 6: CT UNCERTAIN-only verdicts (Diagnosed)**
CT fires but claim_type from agent output often doesn't match FINDING_SUPPORTS
or FINDING_REFUTES sets, and evidence items frequently fail file:line verification
against modified code. Both conditions produce UNCERTAIN regardless of agent quality.
Partial fix: logging. Full fix requires structured output schema enforcement.

**SymPy Verification of Top 4 Run 9 Claims:**
- IM_F001 (sensitivity_decay polarity, 63x): ALREADY FIXED in Run 5 (AW-1)
- IM_F005 (chain_exhaustion double-counting, 52x): ALREADY EXAMINED (SY-3)
- false_positive_rate off-by-one: TRIVIAL (11 vs 10 rounds, consistent)
- strict inequality boundary: UNLOCATED (no specific code reference)
All top-restated findings are either resolved or trivial. 84.5% churn confirmed.

## Churn Analysis

Top 5 most-restated findings:
- IM_F001: 63×
- IM_F002: 63×
- IM_F003: 62×
- IM_F004: 58×
- IM_F005: 52×

Novel findings per round:
```
[34, 12, 7, 1, 5, 4, 8, 0, 3, 0, 4, 0, 0, 5, 5, 1, 1, 1, 0, 0]
```

Novelty effectively exhausted by Round 13.

## Run 10 Action Items

1. ~~Fix `continue` bypass — convergence check must run every round~~ DONE
2. ~~Fix hardcoded `tau_sim=0.8` — remove explicit kwarg~~ DONE
3. ~~Investigate/fix DM FSM terminal failure at R5~~ DONE (no_exclusion_mode)
4. ~~Investigate B-Cell non-firing~~ DONE — f-string escape bugs in _verify_z3 and _verify_statistical
5. ~~Investigate CT UNCERTAIN-only verdicts~~ DIAGNOSED — claim_type mismatch + evidence verification failures
6. ~~Fix silent exception swallowing in pipeline~~ DONE — logging.warning replaces pass
7. ~~Add finding-ID convergence detection~~ DONE — 3 consecutive zero-novel rounds
8. Switch runtime to Python 3.13 (between runs)
9. Cross-reference 65 unique findings against already-applied fixes — SymPy confirmed top 4 are stale
