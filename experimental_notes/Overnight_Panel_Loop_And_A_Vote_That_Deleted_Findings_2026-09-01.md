# Overnight: a panel loop, and a vote that could delete findings

**2026-09-01, 06:10 BST.** Fix the parser, re-run, loop under panel review until the convergence is honest. Two panel rounds ran; both refuted my work; the most serious defect found all night was not the one I was looking for.

## 1. The headline — a model could delete a finding by repeating itself

`FindingRegistry.add_verdict` appends every verdict row unconditionally, and `auto_resolve_contested` (`reference_runner_v2.py:2209`) counts **rows**, not distinct models:

```
challenges = sum(1 for v in recent_verdicts if v.get("verdict") == "CHALLENGE")
if challenges >= 3 and confirms == 0:   ->  auto-refute
```

Reproduced against live code: **one model, one reply, three CHALLENGE lines → 3 rows, 1 distinct model, a severity-0.9 finding auto-refuted.** Verified **pre-existing at real HEAD** (loaded from git): three plain repeated lines already do it.

In a framework whose founding principle is **tools decide, not votes**, a model that deletes a finding by repeating itself is the failure the project exists to prevent, sitting inside the project.

**Has it ever fired?** No evidence, on a slice covering just over half the archive: 2 archived auto-refutals on ≥3 challenge rows, **both multi-model, zero single-model**. The scan reaches 28 of 50 real reports (**56%**, Wilson [42.3%, 68.8%]). The path is real and reproducible; it has not been observed firing.

**Repair (CC2's, adopted):** per-reply dedupe on `(verdict, canonical_id)` keeping the longest evidence, plus a five-label whitelist. **6,721 verdicts** vs HEAD's 6,070 — **+651 recovered, 9.7%**, Wilson [9.00%, 10.42%].

**Residual, open:** the dedupe is per **reply**. A model challenging the same finding across three **rounds** still auto-refutes, because the tally still counts rows. Closing that changes a convergence-adjacent component and was not attempted unreviewed overnight. **First item for the next panel round.**

## 2. What the panel caught in me

Three wrong-artefact measurements, each caught by a reviewer rather than by me:

| claim | measured on | should have been | error |
|---|---|---|---|
| "1 of 2,401 replies affected" | a regex proxy | the parser I was changing | **45×** |
| rehearsal 4→17 findings | full replies | (both valid; archive gives 12) | ambiguity |
| "the `**` blind spot" | raw reply text | text after `runner_core.py:440` strips `**` | premise false |

The third is the sharpest: **the `**` blind spot never existed.** Fable made the same error independently, having checked `_normalise_field_labels` rather than line 440.

## 3. Two reviewers, opposite verdicts, settled by execution

Round 1: **Fable VERIFIED** the verdict fix, stating it had "verified the safety interlocks: tallies all reduce to distinct models". **CC2 REFUTED** it and was right. I settled it by running the code, not by preferring a reviewer — the project's own principle applied to its reviewers. **This is the case against ever accepting a single verification.**

## 4. Composability, as asked

- **Fix 2 variants:** CC2's subsumed Fable's — measured head-to-head it dominated on every adversarial case (fenced phantom 0.70→0.30, review summary 1→0, repeated heading 2→1).
- **Guard variants (a)/(b)/(c):** three thresholds on **one axis**, strictly ordered by trigger-set inclusion. Not exclusive, not complementary.
- **(d) is off that axis** — it asks the question at *heading* granularity rather than *reply* granularity, which is why it is the only variant that gets both the genuine case and the summary case right.

## 5. The defect no guard variant touched

`#{1,6}` matches a **Python comment**. A pasted tool transcript containing `# F001: Check the pruning logic` minted spurious severity-0.5 findings — **12 across two `falsifier_matrix_2026-06-06` replies: real models, June 2026, real data.** Older and larger than the defect the guard was written for. Now **0**.

## 6. Machinery that had never run

The parser repairs moved findings into the registry, which gave the downstream machinery something to work on for the first time:

| mechanism | run 1 | run 2 |
|---|---|---|
| registry entries, round 0 | 8 | **14** |
| corrected copies unmatched | **19** | **0** |
| discrimination control verdicts | 1 | **11** |
| mechanical faults detected | 0 | **4** |
| z3 SMT-grounded proofs | 0 | **2** (one proof, one counterexample) |

**The discrimination control ran at scale for the first time** and produced a measurement the project exists to produce: of 11 falsifiers tested, only **4 genuinely discriminate — 36.4%**, Wilson [15.2%, 64.6%]. Three fire just as hard against a *corrected* copy, so they are not testing their claim; four never reach a verdict. Those findings are escalated, **not closed** — tools deciding.

**The macrophage is clean by design, not silent:** 44 verdicts received, 0 anomalies. Its run-1 alarm ("91% of verdicts are UNCERTAIN") was real signal about the parser defect, now gone.

## 7. Unextracted work recovered

A worktree at `/private/tmp/cdsfl_review_89557` (HEAD `657b02c`, 2026-08-30) still held uncommitted work existing nowhere else: a **142-line test absent from main**, plus 43 and 131 lines in two runner files. `/private/tmp` clears on reboot — one restart from lost. Preserved verbatim to `experimental_notes/unextracted_sandbox_2026-08-30/`, **nothing applied**, worktree left in place pending a ruling. Both files changed substantially since, so it needs a read, not a merge.

## 8. The deliverable: the decay curve now exists

The previous run converged at round 3 on a **VACUOUS CURVE** — zero criticals in every round, `gamma_critical` undefined rather than low, the gate itself warning that "a clean target and a broken severity classifier look alike from here".

| | gamma_critical series |
|---|---|
| run 1 | `[0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` — flat zero, **converged anyway** |
| run 2 | `[0.0, 0.0, 1.0, 0.622, 0.622, 0.536, 0.536, 0.527, 0.527]` — **a real decay curve** |

Run 2 decays from 1.0 toward 0.527, mean 0.624 over seven non-zero values, against a 0.30 threshold. **The decay side of the two-sided gate is satisfied.** The run stays open because the *other* side is not: `novel_crit_recent` moved `[0,0,1] → [0,1,0] → [1,0,0]`, a critical passing through the three-round window and resetting the zero-new-critical streak each time.

That is the whole point. **The gate is open because criticals are still arriving, not because the curve does not exist.** An honest evaluation, on evidence, in both directions.

Supporting evidence that the pipeline is closing the loop, not merely accumulating:

- **3 findings CLOSED** on `verified fix, no unresolved challenges` (run 1 closed **zero**)
- **C0028 correctly REFUSED closure** because its falsifier fires on a corrected copy
- unmatched corrected copies **70.4%** [51.5%, 84.1%] → **18.2%** [8.6%, 34.4%], non-overlapping — reduced, **not** eliminated
- z3 produced one grounded **proof** and one grounded **counterexample**; run 1 produced neither

## 9. A limit on what this rehearsal can prove

The simulated panel rates severity **materially lower than the real panel on the same module**. Measured against the real exp45 run, same target:

| | findings | criticals | rate | 95% CI (Wilson) |
|---|---|---|---|---|
| real exp45 | 41 | 12 | **29.3%** | [17.6%, 44.5%] |
| this rehearsal | 35 | 2 | **5.7%** | [1.6%, 18.6%] |

A 5.1x difference. Fisher exact p=0.015, chi-square p=0.019, z-test p=0.008 — **all three significant**, though the intervals still marginally overlap.

**This is a fidelity gap, not a runner defect.** The machinery behaves correctly on the input it is given; the stand-in agents produce lower severities than the real panel models. The consequence matters for how this run should be read: **a clean convergence here validates the MACHINERY, and does not predict the critical dynamics of a live run.** Bench Run 2 should not be planned on the rehearsal's critical rate.

The curve is nonetheless **no longer vacuous**: criticals appeared in rounds 0 and 3 (history `[1, 0, 0, 1]`), where the previous run had zero in every round. The round-3 critical resets the zero-new-critical streak, so convergence cannot occur before round 6 — the run is being held open by genuine findings rather than stopping on an empty condition.

## 10. Status

Suite **4,680 passed, 0 failed**. Canonical tree clean, archive intact at 52,162 lines. All work committed locally, **nothing pushed**.

*Run status at time of writing: round 3, not yet converged — which is itself the point, since the previous run stopped here on a vacuous curve.*
