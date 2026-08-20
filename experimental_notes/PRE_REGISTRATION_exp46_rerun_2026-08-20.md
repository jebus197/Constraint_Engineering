# Pre-registration: the exp46 matched re-run and the clean prospective runs

**DRAFT — awaiting founder approval. Not frozen.**
Drafted 2026-08-20 01:2x BST. Nothing in this document may be changed after the
founder freezes it and before the runs complete. That is the entire point of it.

## Why this exists

DeepSeek raised it in the 2026-08-19 panel and no other panellist did:

> "Selecting exp46 because it had the narrowest margin is post-hoc; that
> selection must be frozen now."

The matched experiment was chosen **after** seeing that exp46 had the narrowest
convergence margin in the arc (gamma_critical 0.3357 against a 0.30 threshold).
A reviewer is entitled to ask whether the test was picked because it would give
the wanted answer. Writing the choice and the endpoints down before the run is
the only answer to that, and it costs nothing.

## 1. What is being tested

Between 12 April and 19 August 2026 the duplicate discriminator flagged
**97.4%** of finding pairs as near-duplicates (measured; the pipeline's own log
records 97.1% over four months). Every model was told at the start of every round
that essentially all of its prior findings were duplicates and must be proven
distinct or withdrawn.

**The claim under test:** that the repairs landed on 19–20 August restore normal
throughput, and that convergence still occurs when the panel is no longer under a
standing instruction to stop reporting.

## 2. The runs, fixed in advance

| # | Run | Role | Chosen because |
|---|---|---|---|
| 1 | **exp46 re-run**, same target, same config | matched before/after | founder ruling 2026-08-19, after a panel split. Same target isolates the harness change from the target change. |
| 2 | **exp50** (physics, built, never run) | first clean prospective run | never contaminated |
| 3 | **exp51** (biology, built, never run) | second clean domain | one clean run cannot separate the fix effect from a domain or seed effect (DeepSeek) |

**Three live runs.** On two, this is a pilot and must be called one.

CC2 argued for exp44 instead of exp46 (13 rounds, so the churn floor can fire;
the only run where counterfactual repair produced both labels). That argument is
recorded and was not taken. The founder ruled exp46 on cost and on it exercising
every fix without risking a pristine target.

## 3. Endpoints, declared before the runs

**Primary.** Does exp46 re-run converge, and at which round?
Archived: converged at round 5 by CRITICAL_QUIESCENCE (two-sided gate),
gamma_critical 0.3357, 27 findings.

**Secondary, all pre-declared:**
1. Duplicate flagging rate. Predicted to fall from ~97% to roughly 15–25%
   (measured offline: 98.0% -> 21.4% on exp46's own 351 pairs).
2. Findings surviving the immune pipeline. Predicted to rise from ~3%.
3. R_k corroboration compliance: PASS/WARN/FAIL/SKIP. Baseline after the reader
   repair: 37.1 / 3.1 / 51.9 / 7.8 percent.
4. Merges written. Predicted **zero**, because the vote paths are removed and no
   tool verdict is wired yet.
5. rho_avg and whether the shadow floor of 6 would have fired.

## 4. What would count as a failure — declared now, not after

- **exp46 does not converge within its round budget.** This is a real possible
  outcome, not a formality. If suppression was contributing to convergence,
  removing it may mean the discovery curve does not flatten in time. That result
  would be a finding about round budgets, not a refutation of the model.
- **Duplicate flagging stays above 50%.** The clamp did not do what the offline
  measurement says it does.
- **Throughput does not rise.** The 97% removal was not the binding constraint.
- **Compliance does not improve** once the R_k correction reaches prompts.

## 5. What may NOT be changed after freezing

The matched experiment; the endpoints in §3; the failure conditions in §4; the
convergence configuration of the exp46 re-run. If any must change, the change is
recorded here with its date and reason, and the run is reported as amended.

## 6. Known risks, recorded in advance

- **NO_SCORE has never executed in a live run.** It landed 2026-08-01; the arc ran
  27–29 July; it appears zero times in every archived log. 325 unit tests, no live
  execution. exp50 will be its first.
- **On prose targets NO_SCORE short-circuits before the S\* check**, so a measured
  complexity value cannot reach a prose run at all.
- **Nothing will merge**, by design, until counterfactual repair is plumbed to the
  merge site. Findings that would have merged stay OPEN and non-blocking with
  `merge_blocked_reason` recorded.

---
Written under CDSFL note standard v1.4 (13 August 2026, Rule 24 added 16 August).
