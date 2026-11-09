# The canonical interval helper, and the correction of a correction

9 November 2026, 14:55 GMT

## What this records

A producer written on 9 November 2026, `scripts/which_of_b21s_five_steps_are_built_2026-11-09.py`, defined a local interval helper `_iv` that returned the **Wilson interval twice** where the project's other 46 helpers return Wilson and then Clopper-Pearson. A guard that loads and executes every such helper refused the commit carrying it. The helper has been replaced by the canonical implementation, lifted byte-exact; the figures already published from it are unchanged; and a correction reported to the founder on the night of 8 November is **withdrawn as overstated**.

Status of every claim below: **MEASURED** unless marked otherwise.

## The defect, and its exact extent

| | Broken helper | Canonical helper |
|---|---|---|
| First pair | Wilson, written-out formula | Wilson, `statsmodels` |
| Second pair | **Wilson again**, `statsmodels` | **Clopper-Pearson**, `scipy.stats.beta.ppf` |
| Cross-check magnitude | Wilson vs Wilson | worse of (Wilson spread, Clopper-Pearson spread) |
| At `n == 0` | `(0.0, 0.0)` | `(0.0, 1.0)` |

`bench/tests/test_an_interval_rests_on_two_routes_2026-11-03.py` builds a dictionary of every `_iv` defined under `scripts/`, calls each at the same `(k, n)`, and compares all 4 returned numbers. A Wilson pair occupying the Clopper-Pearson slot disagrees with the other 46 whatever its values are, so **6 parametrised cases failed** and the gate refused the commit. That guard did exactly what it exists to do.

## The correction of the correction

The failure was first reported as making every agreement figure from this producer **near-tautological**, on the reasoning that 2 correct implementations of 1 formula must agree. That is too strong, and the project's own instruments refute it.

`scripts/counting_imports_ranks_producers_backwards_2026-11-03.py` is the project's route predicate. Executed against the broken file it returns:

```
Wilson   2   ['statsmodels proportion_confint', 'written-out algebra']
```

and its guard carries `test_the_same_quantity_twice_is_a_cross_check`, which asserts that this exact pairing **is** a cross-check. So the pairing is the *weaker* kind — 1 formulation, 2 implementations — which the independence rule of 31 October 2026 already classifies as such. It is not nothing, and "near-tautological" may not be said of it.

SymPy confirms the 2 routes compute the same quantity: with `p = k/n`, `d = 1 + z²/n`, the written-out lower bound minus the closed form simplifies to **0**.

**What was genuinely absent is Clopper-Pearson, computed nowhere in the file.** That is the whole defect.

## Why the published figures did not move

The canonical helper returns `max(wdiff, cdiff)`. At 1 of 5 the Wilson spread dominates, so the reported magnitude is **1.110223e-16 before and after**. The Wilson bounds were correct throughout.

What the repair *adds* is the second interval:

| Quantity | Wilson | Clopper-Pearson |
|---|---|---|
| 1 of 5 steps built | [0.036224, 0.624465] | **[0.005051, 0.716418]** |
| 1 of 6 live-harness files | [0.030053, 0.563503] | **[0.004211, 0.641235]** |

Verified on 3 routes — `statsmodels` `method="beta"`, `scipy.stats.beta.ppf`, and an independently written mpmath bisection of the regularised incomplete beta at 40 digits — agreeing to **1.110e-16**, i.e. double-precision epsilon.

## The empty denominator: `(0.0, 0.0)` was wrong

With `n == 0` the binomial likelihood is 1 for every `p`, so no `p` is excluded and `[0, 1]` is the only honest interval. `(0.0, 0.0)` asserts certainty that the proportion is 0 from no data. `statsmodels` returns `(nan, nan)` here, which is why the canonical helper short-circuits rather than printing `nan`. The guard pinned the wrong value and now pins `(0.0, 1.0)` with the derivation beside it.

## Containment cannot catch this; strict width can

An interval contains itself, so a containment assertion **passes on the broken form at 741 of 741 interior grid points**. The discriminating property is strict width: Clopper-Pearson is strictly wider than Wilson wherever `0 < k < n`.

Measured over `2 <= n < 40`:

- strictly wider at **741 of 741** interior points;
- a helper returning Wilson twice is rejected at **741 of 741 = 1.000000**, Wilson [0.994843, 1.000000], Clopper-Pearson [0.995034, 1.000000].

Both figures are produced by `bench/tests/test_which_of_b21s_five_steps_are_built_2026-11-09.py` itself, which walks the grid rather than 5 convenient points for 2 reasons: `measured-rate-travels-with-its-script` requires committed code behind a quoted rate, and the same loop run against a deliberately broken helper is the anti-vacuity proof. Cost 5.24 s against a board of roughly 4000 s.

**4 of 4 reversions red**: the Wilson-twice form, the `(0.0, 0.0)` empty denominator, a 1-character fork of the canonical body, and the Clopper-Pearson computed but not printed.

## The canonical body is shared, not re-derived

Lifted byte-exact from `scripts/what_the_commit_gate_actually_costs_over_time_2026-11-08.py`, sha256 of the function source beginning `5c0ff108ca6d5966` — 1 of 16 identical copies among 18 textual variants across 47 files. The explanation sits in a **comment above** the `def`, deliberately, so the function's own source segment stays byte-identical and the file counts as the 17th user rather than a 19th variant. A guard pins the hash equality in both directions and names the re-derivation step if the canonical body itself ever changes.

The local `wilson()` and its `Z` constant were **removed** with the swap, because after it nothing reached them — `additive-standard`'s symmetric clause.

## 3 process errors, each caught by an instrument rather than by reading

1. **A hand-typed mutation anchor.** The harness named `TestItRuns::test_it_reports_all_five_steps`, which does not exist; pytest exited 4 with *no tests ran*, which reads as a harness fault, not a bad anchor. It now derives anchors from `--collect-only` and names any that fail to resolve. This is `feedback_a_mutation_harness_must_derive_its_anchors_2026-11-04` recurring.
2. **Sorting a list that was not sorted.** `sorted(set(...))` over the `GUARDS` block in `hooks/pre-commit` turned a 2-entry addition into **131 insertions, 129 deletions**, destroying a grouping that is by commit, not alphabetical. Restored; the real diff is **3 added, 1 removed**, 232 → 234 entries, 0 duplicates.
3. **Editing the tree under a live board, twice.** `feedback_never_edit_the_tree_while_a_commits_board_runs_2026-11-02`. The board read a `GUARDS` list mid-rewrite and appended `{"seconds":705,"exit":0,"head":"fc9edaf7"}` to `.cdsfl_tmp/precommit_durations.jsonl`. **The row is kept, not pruned** ("point, never prune"): dropping it gives 11 of 12 = 0.916667 against 12 of 13 = 0.923077, so it carries no argument either way. A third touch followed — `scripts/blocker_triage.py` writes by default and has a `--check-only` flag that was not used.

## A stale figure corrected in the same pass

The master task list asserted, **in the present tense**, that the gate exceeds its stated limit on *7 of 8* recorded runs. The ledger has grown 8 → 14 rows because this session's own boards append to the file being measured — the same self-measurement that forced a withdrawal on 8 November, reappearing in the **denominator** rather than the mean. Re-stated as **12 of 13 = 0.923077**, Wilson [0.666860, 0.986290], Clopper-Pearson [0.639703, 0.998054], with the 8 November reading preserved in the past tense beside it.

The lesson is narrower than "the figure was wrong": it was correct when written. **A present-tense figure over a growing ledger goes stale by being correct at the time.**

## The open queue: 20 entries, and the resume pointer cannot help

Read while the board ran, so no tree was touched.

- `scripts/the_resume_pointer_names_his_decisions_as_work_2026-11-08.py`: of the 12 decisions in `Decisions_Awaiting_You_2026-11-09_GENERATED.md`, **0 of 12 = 0.000000** carry the `BLOCKED` state the list reserves for them, Wilson [0.000000, 0.242494], Clopper-Pearson [0.000000, 0.264648]. They carry `OPEN`, so the resume pointer names them as unstarted work. **B21 is decision 1 of 12.**
- B56, B107, B134 each ask the founder directly. **B132** states *STILL OPEN FOR THAT REASON ALONE* — held pending B104. B22 is his panel question. C0001 records that closing it is his judgement. B123 is `STATUS: REPORTED`, left failing because the failure is the alert he asked for.
- `scripts/how_many_open_defects_are_already_fixed_2026-11-08.py`: **5 of 6 = 0.833333** probed defect records are already satisfied, Wilson [0.436497, 0.969947]; **4 of 6 = 0.666667** were satisfied before 8 November, Wilson [0.299993, 0.903229].
- The single genuinely-open record, `the-classifier-logs-no-pre-syntax-confidence`, is also his: `scripts/the_syntax_clause_was_never_built_2026-11-08.py` finds **4 of 4** assignments to `llm_confidence` derive from the model's reply or a constant, **0 of 4** from any other signal, and the value gates `should_override` at `bench/immune_agents.py:5474`. The clause was never built, and building it changes routing.

## One live figure, and a refuted hypothesis

B123 exists because the founder asked to be told if the list stopped terminating. Its recorded ratio is **R = 0.914692, [0.752709, 1.111534]** (4 November). Re-measured 9 November via `bench/tests/test_task_list_burndown_2026-09-11.py`: **R = 0.9072, [0.7545, 1.0908]**. Still above 1, still failing; the upper bound has **narrowed** from 1.1115, so movement is toward clearing. The point estimate stays below 1 and no test rejects termination. The same run reports **B11 and C29 marked DONE while naming that failing test as evidence** — B107's subject, awaiting his ruling.

**HYPOTHESIS REFUTED.** That the alert was hidden from the founder by a frozen literal. `scripts/rebuild_morning_report_markdown_2026-10-30.py` does carry `R = 0.7791` as a hardcoded table row — but `Morning_Report_2026-11-08_GENERATED.md` computes the ratio live, states *186 entries added against 207 closed*, R = 0.8986, interval 0.7374 to 1.0950, exact test 0.3130, names its producer, and carries both B107 and B123. The `0.7791` literal reaches only the correctly dated 30 October report. The alert reaches him as designed.

## What is owed

Nothing of the repair. Outstanding and queued behind the running board: B123's recorded figure updated to 0.9072, B21 re-parked with `--detail` instead of the classifier's fallback reason, and the commit message merged so it accounts for every staged file per entry B128's habit.

Written under CDSFL note standard v1.9 (1 November 2026).
